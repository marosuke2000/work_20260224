"""
ポモドーロタイマー with ゲーミフィケーション要素
- 経験値システム（XP & レベルアップ）
- 達成バッジシステム
- ストリーク表示
- 週間/月間統計
"""
from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
from collections import defaultdict
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pomodoro.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# データベースモデル
class PomodoroSession(db.Model):
    """ポモドーロセッションの記録"""
    id = db.Column(db.Integer, primary_key=True)
    duration = db.Column(db.Integer, nullable=False)  # 秒単位
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    xp_earned = db.Column(db.Integer, default=0)

class UserStats(db.Model):
    """ユーザー統計情報"""
    id = db.Column(db.Integer, primary_key=True)
    total_xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    total_sessions = db.Column(db.Integer, default=0)
    total_focus_time = db.Column(db.Integer, default=0)  # 秒単位
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_session_date = db.Column(db.Date, nullable=True)

class Achievement(db.Model):
    """達成バッジ"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(200))
    icon = db.Column(db.String(50))
    unlocked = db.Column(db.Boolean, default=False)
    unlocked_at = db.Column(db.DateTime, nullable=True)

# ゲーミフィケーション機能
class GamificationSystem:
    """ゲーミフィケーション要素を管理するクラス"""
    
    # レベルアップに必要なXP（累積）
    LEVEL_XP_REQUIREMENTS = {
        1: 0, 2: 100, 3: 250, 4: 500, 5: 850,
        6: 1300, 7: 1850, 8: 2500, 9: 3250, 10: 4100
    }
    
    # ポモドーロ完了時のXP
    XP_PER_POMODORO = 50
    
    # 達成バッジの定義
    ACHIEVEMENTS = [
        {"name": "first_pomodoro", "description": "初めてのポモドーロ完了", "icon": "🎯"},
        {"name": "streak_3", "description": "3日連続でポモドーロ実施", "icon": "🔥"},
        {"name": "streak_7", "description": "7日連続でポモドーロ実施", "icon": "⚡"},
        {"name": "weekly_10", "description": "今週10回完了", "icon": "🌟"},
        {"name": "total_50", "description": "累計50回完了", "icon": "🏆"},
        {"name": "total_100", "description": "累計100回完了", "icon": "👑"},
        {"name": "level_5", "description": "レベル5到達", "icon": "🎖️"},
        {"name": "level_10", "description": "レベル10到達", "icon": "💎"},
    ]
    
    @staticmethod
    def calculate_level(xp):
        """XPからレベルを計算"""
        level = 1
        for lvl, required_xp in sorted(GamificationSystem.LEVEL_XP_REQUIREMENTS.items()):
            if xp >= required_xp:
                level = lvl
            else:
                break
        return level
    
    @staticmethod
    def xp_for_next_level(current_xp):
        """次のレベルまでに必要なXP"""
        current_level = GamificationSystem.calculate_level(current_xp)
        if current_level >= 10:
            return 0  # 最大レベル
        next_level = current_level + 1
        return GamificationSystem.LEVEL_XP_REQUIREMENTS[next_level] - current_xp
    
    @staticmethod
    def check_achievements(stats):
        """達成バッジのチェックと付与"""
        newly_unlocked = []
        
        # 初めてのポモドーロ
        if stats.total_sessions >= 1:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("first_pomodoro"))
        
        # ストリーク関連
        if stats.current_streak >= 3:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("streak_3"))
        if stats.current_streak >= 7:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("streak_7"))
        
        # 累計完了数
        if stats.total_sessions >= 50:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("total_50"))
        if stats.total_sessions >= 100:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("total_100"))
        
        # レベル到達
        if stats.level >= 5:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("level_5"))
        if stats.level >= 10:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("level_10"))
        
        # 今週の完了数チェック
        weekly_count = GamificationSystem._get_weekly_session_count()
        if weekly_count >= 10:
            newly_unlocked.extend(GamificationSystem._unlock_achievement("weekly_10"))
        
        return newly_unlocked
    
    @staticmethod
    def _unlock_achievement(name):
        """達成バッジをアンロック"""
        achievement = Achievement.query.filter_by(name=name).first()
        if achievement and not achievement.unlocked:
            achievement.unlocked = True
            achievement.unlocked_at = datetime.utcnow()
            db.session.commit()
            return [achievement]
        return []
    
    @staticmethod
    def _get_weekly_session_count():
        """今週の完了セッション数を取得"""
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday())
        count = PomodoroSession.query.filter(
            PomodoroSession.completed == True,
            PomodoroSession.timestamp >= datetime.combine(week_start, datetime.min.time())
        ).count()
        return count
    
    @staticmethod
    def update_streak(stats):
        """ストリークを更新"""
        today = datetime.utcnow().date()
        
        if stats.last_session_date is None:
            # 初回セッション
            stats.current_streak = 1
            stats.longest_streak = 1
            stats.last_session_date = today
        elif stats.last_session_date == today:
            # 同日内の追加セッション（ストリークは変わらない）
            pass
        elif stats.last_session_date == today - timedelta(days=1):
            # 連続日
            stats.current_streak += 1
            if stats.current_streak > stats.longest_streak:
                stats.longest_streak = stats.current_streak
            stats.last_session_date = today
        else:
            # ストリーク途切れ
            stats.current_streak = 1
            stats.last_session_date = today

# ルート定義
@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    """統計情報を取得"""
    stats = UserStats.query.first()
    if not stats:
        stats = UserStats()
        db.session.add(stats)
        db.session.commit()
    
    return jsonify({
        'level': stats.level,
        'total_xp': stats.total_xp,
        'xp_to_next_level': GamificationSystem.xp_for_next_level(stats.total_xp),
        'total_sessions': stats.total_sessions,
        'total_focus_time': stats.total_focus_time,
        'current_streak': stats.current_streak,
        'longest_streak': stats.longest_streak
    })

@app.route('/api/complete_session', methods=['POST'])
def complete_session():
    """ポモドーロセッション完了"""
    data = request.json
    duration = data.get('duration', 1500)  # デフォルト25分
    
    # セッション記録
    session = PomodoroSession(
        duration=duration,
        completed=True,
        xp_earned=GamificationSystem.XP_PER_POMODORO
    )
    db.session.add(session)
    
    # 統計更新
    stats = UserStats.query.first()
    if not stats:
        stats = UserStats()
        db.session.add(stats)
    
    stats.total_xp += GamificationSystem.XP_PER_POMODORO
    stats.total_sessions += 1
    stats.total_focus_time += duration
    
    # レベル計算
    old_level = stats.level
    stats.level = GamificationSystem.calculate_level(stats.total_xp)
    level_up = stats.level > old_level
    
    # ストリーク更新
    GamificationSystem.update_streak(stats)
    
    db.session.commit()
    
    # 達成バッジチェック
    newly_unlocked = GamificationSystem.check_achievements(stats)
    
    return jsonify({
        'success': True,
        'xp_earned': GamificationSystem.XP_PER_POMODORO,
        'total_xp': stats.total_xp,
        'level': stats.level,
        'level_up': level_up,
        'current_streak': stats.current_streak,
        'newly_unlocked': [{'name': a.name, 'description': a.description, 'icon': a.icon} 
                          for a in newly_unlocked]
    })

@app.route('/api/achievements')
def get_achievements():
    """達成バッジ一覧を取得"""
    achievements = Achievement.query.all()
    return jsonify([{
        'name': a.name,
        'description': a.description,
        'icon': a.icon,
        'unlocked': a.unlocked,
        'unlocked_at': a.unlocked_at.isoformat() if a.unlocked_at else None
    } for a in achievements])

@app.route('/api/statistics')
def get_statistics():
    """週間/月間統計を取得"""
    today = datetime.utcnow().date()
    
    # 週間統計（過去7日）
    week_start = today - timedelta(days=6)
    weekly_sessions = PomodoroSession.query.filter(
        PomodoroSession.completed == True,
        PomodoroSession.timestamp >= datetime.combine(week_start, datetime.min.time())
    ).all()
    
    # 月間統計（過去30日）
    month_start = today - timedelta(days=29)
    monthly_sessions = PomodoroSession.query.filter(
        PomodoroSession.completed == True,
        PomodoroSession.timestamp >= datetime.combine(month_start, datetime.min.time())
    ).all()
    
    # 日別集計
    weekly_by_day = defaultdict(lambda: {'count': 0, 'total_time': 0})
    for session in weekly_sessions:
        day_key = session.timestamp.date().isoformat()
        weekly_by_day[day_key]['count'] += 1
        weekly_by_day[day_key]['total_time'] += session.duration
    
    monthly_by_day = defaultdict(lambda: {'count': 0, 'total_time': 0})
    for session in monthly_sessions:
        day_key = session.timestamp.date().isoformat()
        monthly_by_day[day_key]['count'] += 1
        monthly_by_day[day_key]['total_time'] += session.duration
    
    # 週間データ整形
    weekly_data = []
    for i in range(7):
        date = week_start + timedelta(days=i)
        day_key = date.isoformat()
        weekly_data.append({
            'date': day_key,
            'count': weekly_by_day[day_key]['count'],
            'total_time': weekly_by_day[day_key]['total_time']
        })
    
    # 月間データ整形
    monthly_data = []
    for i in range(30):
        date = month_start + timedelta(days=i)
        day_key = date.isoformat()
        monthly_data.append({
            'date': day_key,
            'count': monthly_by_day[day_key]['count'],
            'total_time': monthly_by_day[day_key]['total_time']
        })
    
    # 統計計算
    weekly_avg_time = sum(s.duration for s in weekly_sessions) / max(len(weekly_sessions), 1)
    monthly_avg_time = sum(s.duration for s in monthly_sessions) / max(len(monthly_sessions), 1)
    
    return jsonify({
        'weekly': {
            'total_sessions': len(weekly_sessions),
            'total_time': sum(s.duration for s in weekly_sessions),
            'avg_time': weekly_avg_time,
            'data': weekly_data
        },
        'monthly': {
            'total_sessions': len(monthly_sessions),
            'total_time': sum(s.duration for s in monthly_sessions),
            'avg_time': monthly_avg_time,
            'data': monthly_data
        }
    })

def init_db():
    """データベース初期化"""
    with app.app_context():
        db.create_all()
        
        # 達成バッジの初期化
        for achievement_def in GamificationSystem.ACHIEVEMENTS:
            existing = Achievement.query.filter_by(name=achievement_def['name']).first()
            if not existing:
                achievement = Achievement(
                    name=achievement_def['name'],
                    description=achievement_def['description'],
                    icon=achievement_def['icon']
                )
                db.session.add(achievement)
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
