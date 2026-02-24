"""ポモドーロタイマーのユニットテスト"""
import pytest
from timer import PomodoroTimer, TimerState


class TestPomodoroTimer:
    """PomodoroTimerクラスのテスト"""
    
    def test_初期化時の状態(self):
        """初期化時のデフォルト値が正しいか確認"""
        timer = PomodoroTimer()
        
        assert timer.state == TimerState.STOPPED
        assert timer.remaining_seconds == 25 * 60
        assert timer.completed_pomodoros == 0
        assert timer.total_focus_time == 0
    
    def test_カスタム設定での初期化(self):
        """カスタム設定で初期化できるか確認"""
        timer = PomodoroTimer(
            work_duration=10,
            short_break_duration=3,
            long_break_duration=6,
            pomodoros_until_long_break=2
        )
        
        assert timer.work_duration == 10
        assert timer.short_break_duration == 3
        assert timer.long_break_duration == 6
        assert timer.pomodoros_until_long_break == 2
    
    def test_タイマー開始(self):
        """タイマーを開始できるか確認"""
        timer = PomodoroTimer()
        timer.start()
        
        assert timer.state == TimerState.WORKING
        assert timer.remaining_seconds == 25 * 60
    
    def test_tick処理(self):
        """tick処理で時間が減るか確認"""
        timer = PomodoroTimer(work_duration=10)
        timer.start()
        
        # 1秒経過
        finished = timer.tick()
        assert finished is False
        assert timer.remaining_seconds == 9
        assert timer.total_focus_time == 1
    
    def test_タイマー終了判定(self):
        """タイマーが終了するか確認"""
        timer = PomodoroTimer(work_duration=2)
        timer.start()
        
        # 1秒目
        finished = timer.tick()
        assert finished is False
        assert timer.remaining_seconds == 1
        
        # 2秒目
        finished = timer.tick()
        assert finished is False
        assert timer.remaining_seconds == 0
        
        # 3秒目（終了）
        finished = timer.tick()
        assert finished is True
        assert timer.remaining_seconds == 0
    
    def test_作業完了後の短い休憩(self):
        """作業完了後に短い休憩に移行するか確認"""
        timer = PomodoroTimer(
            work_duration=1,
            short_break_duration=5,
            pomodoros_until_long_break=4
        )
        timer.start()
        timer.tick()
        timer.tick()
        
        # 作業完了
        next_state = timer.complete_current_session()
        
        assert next_state == TimerState.SHORT_BREAK
        assert timer.state == TimerState.SHORT_BREAK
        assert timer.completed_pomodoros == 1
        assert timer.remaining_seconds == 5
    
    def test_作業完了後の長い休憩(self):
        """4回の作業完了後に長い休憩に移行するか確認"""
        timer = PomodoroTimer(
            work_duration=1,
            short_break_duration=2,
            long_break_duration=10,
            pomodoros_until_long_break=4
        )
        
        # 4回ポモドーロを完了（作業→休憩のサイクル）
        for i in range(4):
            # 作業セッション
            if i == 0:
                timer.start()  # 最初だけstart()で開始
            timer.tick()
            timer.tick()
            next_state = timer.complete_current_session()
            
            # 4回目の作業完了後は長い休憩になる
            if i == 3:
                assert next_state == TimerState.LONG_BREAK
                assert timer.state == TimerState.LONG_BREAK
                assert timer.completed_pomodoros == 4
                assert timer.remaining_seconds == 10
                break
            
            # 休憩セッション（4回目以外）
            for _ in range(timer.remaining_seconds):
                timer.tick()
            timer.complete_current_session()  # 休憩完了後、作業に戻る
    
    def test_休憩完了後は作業に戻る(self):
        """休憩完了後に作業に戻るか確認"""
        timer = PomodoroTimer(work_duration=10, short_break_duration=1)
        timer.start()
        timer.tick()
        timer.tick()
        timer.complete_current_session()  # 短い休憩へ
        
        assert timer.state == TimerState.SHORT_BREAK
        
        # 休憩完了
        next_state = timer.complete_current_session()
        
        assert next_state == TimerState.WORKING
        assert timer.state == TimerState.WORKING
        assert timer.remaining_seconds == 10
    
    def test_リセット(self):
        """リセット機能が正しく動作するか確認"""
        timer = PomodoroTimer(work_duration=10)
        timer.start()
        timer.tick()
        timer.tick()
        
        timer.reset()
        
        assert timer.state == TimerState.STOPPED
        assert timer.remaining_seconds == 10
    
    def test_残り時間取得(self):
        """残り時間を分秒で取得できるか確認"""
        timer = PomodoroTimer(work_duration=125)  # 2分5秒
        
        minutes, seconds = timer.get_remaining_time()
        
        assert minutes == 2
        assert seconds == 5
    
    def test_進捗率取得_作業中(self):
        """作業中の進捗率を取得できるか確認"""
        timer = PomodoroTimer(work_duration=100)
        timer.start()
        
        # 初期状態（0%）
        assert timer.get_progress_percentage() == 0.0
        
        # 50秒経過（50%）
        for _ in range(50):
            timer.tick()
        assert timer.get_progress_percentage() == 0.5
        
        # 100秒経過（100%）
        for _ in range(50):
            timer.tick()
        assert timer.get_progress_percentage() == 1.0
    
    def test_進捗率取得_休憩中(self):
        """休憩中の進捗率を取得できるか確認"""
        timer = PomodoroTimer(work_duration=1, short_break_duration=10)
        timer.start()
        timer.tick()
        timer.tick()
        timer.complete_current_session()  # 休憩へ
        
        # 休憩開始時（0%）
        assert timer.get_progress_percentage() == 0.0
        
        # 5秒経過（50%）
        for _ in range(5):
            timer.tick()
        assert timer.get_progress_percentage() == 0.5
    
    def test_集中時間の計算(self):
        """総集中時間が正しく計算されるか確認"""
        timer = PomodoroTimer(work_duration=10, short_break_duration=5)
        timer.start()
        
        # 10秒作業
        for _ in range(10):
            timer.tick()
        
        assert timer.total_focus_time == 10
        
        timer.complete_current_session()  # 休憩へ
        
        # 5秒休憩（集中時間は増えない）
        for _ in range(5):
            timer.tick()
        
        assert timer.total_focus_time == 10
    
    def test_集中時間のフォーマット_分のみ(self):
        """集中時間が60分未満の場合のフォーマット確認"""
        timer = PomodoroTimer()
        timer.total_focus_time = 30 * 60  # 30分
        
        formatted = timer.get_focus_time_formatted()
        
        assert formatted == "30分"
    
    def test_集中時間のフォーマット_時間と分(self):
        """集中時間が60分以上の場合のフォーマット確認"""
        timer = PomodoroTimer()
        timer.total_focus_time = 90 * 60  # 1時間30分
        
        formatted = timer.get_focus_time_formatted()
        
        assert formatted == "1時間30分"
    
    def test_状態ラベル取得(self):
        """状態ラベルが正しく取得できるか確認"""
        timer = PomodoroTimer()
        
        assert timer.get_state_label() == "停止中"
        
        timer.start()
        assert timer.get_state_label() == "作業中"
        
        timer.tick()
        timer.tick()
        timer.complete_current_session()
        assert timer.get_state_label() == "休憩中"
    
    def test_停止中のtick(self):
        """停止中にtickを呼んでも変化しないことを確認"""
        timer = PomodoroTimer(work_duration=10)
        
        finished = timer.tick()
        
        assert finished is False
        assert timer.remaining_seconds == 10
        assert timer.total_focus_time == 0
