"""ポモドーロタイマーのコアロジック"""
from enum import Enum
from typing import Optional


class TimerState(Enum):
    """タイマーの状態"""
    STOPPED = "stopped"
    WORKING = "working"
    SHORT_BREAK = "short_break"
    LONG_BREAK = "long_break"
    COMPLETED = "completed"


class PomodoroTimer:
    """ポモドーロタイマーのロジッククラス"""
    
    def __init__(
        self,
        work_duration: int = 25 * 60,
        short_break_duration: int = 5 * 60,
        long_break_duration: int = 15 * 60,
        pomodoros_until_long_break: int = 4
    ):
        """
        Args:
            work_duration: 作業時間（秒）
            short_break_duration: 短い休憩時間（秒）
            long_break_duration: 長い休憩時間（秒）
            pomodoros_until_long_break: 長い休憩までのポモドーロ回数
        """
        self.work_duration = work_duration
        self.short_break_duration = short_break_duration
        self.long_break_duration = long_break_duration
        self.pomodoros_until_long_break = pomodoros_until_long_break
        
        self.state = TimerState.STOPPED
        self.remaining_seconds = work_duration
        self.completed_pomodoros = 0
        self.total_focus_time = 0  # 総集中時間（秒）
    
    def start(self) -> None:
        """タイマーを開始"""
        if self.state == TimerState.STOPPED:
            self.state = TimerState.WORKING
            self.remaining_seconds = self.work_duration
    
    def tick(self) -> bool:
        """
        1秒経過を処理
        
        Returns:
            bool: タイマーが終了した場合True
        """
        if self.state == TimerState.STOPPED or self.state == TimerState.COMPLETED:
            return False
        
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            
            # 作業中は集中時間を加算
            if self.state == TimerState.WORKING:
                self.total_focus_time += 1
            
            return False
        else:
            # タイマー終了
            return True
    
    def complete_current_session(self) -> TimerState:
        """
        現在のセッションを完了し、次の状態に移行
        
        Returns:
            TimerState: 次の状態
        """
        if self.state == TimerState.WORKING:
            self.completed_pomodoros += 1
            
            # 長い休憩か短い休憩か判定
            if self.completed_pomodoros % self.pomodoros_until_long_break == 0:
                self.state = TimerState.LONG_BREAK
                self.remaining_seconds = self.long_break_duration
            else:
                self.state = TimerState.SHORT_BREAK
                self.remaining_seconds = self.short_break_duration
        
        elif self.state in (TimerState.SHORT_BREAK, TimerState.LONG_BREAK):
            # 休憩終了後は作業に戻る
            self.state = TimerState.WORKING
            self.remaining_seconds = self.work_duration
        
        return self.state
    
    def reset(self) -> None:
        """タイマーをリセット"""
        self.state = TimerState.STOPPED
        self.remaining_seconds = self.work_duration
    
    def get_remaining_time(self) -> tuple[int, int]:
        """
        残り時間を取得
        
        Returns:
            tuple[int, int]: (分, 秒)
        """
        minutes = self.remaining_seconds // 60
        seconds = self.remaining_seconds % 60
        return (minutes, seconds)
    
    def get_progress_percentage(self) -> float:
        """
        進捗率を取得（0.0 〜 1.0）
        
        Returns:
            float: 進捗率
        """
        if self.state == TimerState.WORKING:
            total = self.work_duration
        elif self.state == TimerState.SHORT_BREAK:
            total = self.short_break_duration
        elif self.state == TimerState.LONG_BREAK:
            total = self.long_break_duration
        else:
            return 0.0
        
        if total == 0:
            return 0.0
        
        return (total - self.remaining_seconds) / total
    
    def get_focus_time_formatted(self) -> str:
        """
        総集中時間をフォーマットして取得
        
        Returns:
            str: "X時間Y分" 形式
        """
        hours = self.total_focus_time // 3600
        minutes = (self.total_focus_time % 3600) // 60
        
        if hours > 0:
            return f"{hours}時間{minutes}分"
        else:
            return f"{minutes}分"
    
    def get_state_label(self) -> str:
        """
        状態のラベルを取得
        
        Returns:
            str: 状態ラベル
        """
        labels = {
            TimerState.STOPPED: "停止中",
            TimerState.WORKING: "作業中",
            TimerState.SHORT_BREAK: "休憩中",
            TimerState.LONG_BREAK: "休憩中",
            TimerState.COMPLETED: "終了"
        }
        return labels.get(self.state, "不明")
