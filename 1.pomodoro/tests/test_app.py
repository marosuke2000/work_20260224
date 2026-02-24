"""Flaskアプリケーションのユニットテスト"""
import pytest
from app import app


@pytest.fixture
def client():
    """テスト用のFlaskクライアントを作成"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestFlaskApp:
    """Flaskアプリケーションのテスト"""
    
    def test_index_route_exists(self, client):
        """/ ルートが存在するか確認"""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_returns_html(self, client):
        """/ ルートがHTMLを返すか確認"""
        response = client.get('/')
        assert response.content_type == 'text/html; charset=utf-8'
    
    def test_index_contains_title(self, client):
        """/ ルートがポモドーロタイマーのタイトルを含むか確認"""
        response = client.get('/')
        assert 'ポモドーロタイマー' in response.data.decode('utf-8')
    
    def test_index_contains_timer_elements(self, client):
        """/ ルートがタイマー要素を含むか確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        
        # タイマー表示要素
        assert 'timer-value' in html
        assert 'timer-circle' in html
        assert 'timer-state' in html
        
        # ボタン要素
        assert 'btn-start' in html
        assert 'btn-reset' in html
    
    def test_index_includes_css(self, client):
        """/ ルートがCSSファイルを読み込むか確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '/static/css/style.css' in html
    
    def test_index_includes_js(self, client):
        """/ ルートがJavaScriptファイルを読み込むか確認"""
        response = client.get('/')
        html = response.data.decode('utf-8')
        assert '/static/js/timer.js' in html
    
    def test_static_css_exists(self, client):
        """/static/css/style.css が存在するか確認"""
        response = client.get('/static/css/style.css')
        assert response.status_code == 200
        assert 'text/css' in response.content_type
    
    def test_static_js_exists(self, client):
        """/static/js/timer.js が存在するか確認"""
        response = client.get('/static/js/timer.js')
        assert response.status_code == 200
        # JavaScriptファイルはtext/javascriptまたはapplication/javascript
        assert 'javascript' in response.content_type.lower() or \
               'text/plain' in response.content_type.lower()
    
    def test_404_for_nonexistent_route(self, client):
        """存在しないルートで404が返るか確認"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
