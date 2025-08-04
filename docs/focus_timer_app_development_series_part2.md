# 🏢 스크립트에서 엔터프라이즈로: FocusTimer.app 개발기 (Part 2 엔터프라이즈 기능편)

## 📋 목차

- [엔터프라이즈 요구사항 분석](#-엔터프라이즈-요구사항-분석)
- [웹 대시보드 시스템 설계](#-웹-대시보드-시스템-설계)
- [다중 사용자 관리 시스템](#-다중-사용자-관리-시스템)
- [실시간 데이터 동기화](#-실시간-데이터-동기화)
- [고급 통계 및 분석 시스템](#-고급-통계-및-분석-시스템)
- [API 통합 및 확장성](#-api-통합-및-확장성)
- [보안 강화 및 권한 관리](#-보안-강화-및-권한-관리)
- [결론 및 다음 편 예고](#-결론-및-다음-편-예고)

---

## 🎯 엔터프라이즈 요구사항 분석

### **개인용에서 기업용으로의 전환**

개인용 FocusTimer가 성공적으로 개발되면서, 기업과 조직에서도 사용하고 싶다는 요청이 늘어났습니다. 하지만 개인용 버전은 기업 환경에서 사용하기에는 여러 한계점이 있었습니다:

#### **문제점 1: 중앙 관리의 부재**

```python
# 개인용의 한계
class PersonalFocusTimer:
    def __init__(self):
        self.user_data = {}  # 로컬에만 저장
        self.settings = {}   # 개인별 설정
        # ❌ 중앙 관리 불가능
        # ❌ 조직 정책 적용 불가
        # ❌ 사용자 간 데이터 공유 불가
```

#### **문제점 2: 실시간 모니터링 부재**

```python
# 개인용 모니터링의 한계
def monitor_user_activity():
    # 로컬에서만 활동 추적
    # ❌ 관리자가 실시간으로 확인 불가
    # ❌ 조직 전체 통계 불가능
    # ❌ 이상 징후 감지 불가
```

#### **문제점 3: 확장성 부족**

```python
# 개인용 확장성 한계
class PersonalSystem:
    def __init__(self):
        self.max_users = 1  # 단일 사용자만 지원
        # ❌ 다중 사용자 지원 불가
        # ❌ 조직 단위 관리 불가
        # ❌ 외부 시스템 연동 불가
```

### **엔터프라이즈 요구사항 정의**

#### **핵심 요구사항**

1. **중앙 집중식 관리**: 조직 전체의 FocusTimer 사용 현황 관리
2. **실시간 모니터링**: 사용자 활동 실시간 추적 및 알림
3. **다중 사용자 지원**: 수백 명의 사용자 동시 지원
4. **고급 통계**: 조직 단위 생산성 분석 및 리포트
5. **API 통합**: 기존 기업 시스템과의 연동
6. **보안 강화**: 기업급 보안 및 권한 관리

---

## 🌐 웹 대시보드 시스템 설계

### **1단계: 웹 아키텍처 설계**

#### **Flask 기반 웹 서버 구조**

```python
# enterprise_web/focus_timer_enterprise_web.py
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import redis
import json
import threading
import time
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///enterprise_focus_timer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
redis_client = redis.Redis(host='localhost', port=6379, db=0)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    """사용자 모델"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    department = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    # 관계 설정
    focus_sessions = db.relationship('FocusSession', backref='user', lazy=True)
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True)

class FocusSession(db.Model):
    """집중 세션 모델"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime)
    duration = db.Column(db.Integer)  # 분 단위
    status = db.Column(db.String(20), default='active')  # active, completed, interrupted
    problem_id = db.Column(db.String(50))
    productivity_score = db.Column(db.Float)
    interruptions = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### **2단계: 실시간 모니터링 시스템**

#### **WebSocket 기반 실시간 업데이트**

```python
@socketio.on('connect')
def handle_connect():
    """클라이언트 연결 처리"""
    if current_user.is_authenticated:
        join_room(f'user_{current_user.id}')
        if current_user.role in ['admin', 'manager']:
            join_room('admin_dashboard')

        # 현재 상태 전송
        emit('user_status', {
            'user_id': current_user.id,
            'username': current_user.username,
            'status': 'online',
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True)

@socketio.on('focus_session_start')
def handle_focus_start(data):
    """집중 세션 시작 이벤트"""
    session_data = {
        'user_id': current_user.id,
        'username': current_user.username,
        'start_time': datetime.utcnow().isoformat(),
        'duration': data.get('duration', 25),
        'problem_id': data.get('problem_id')
    }

    # Redis에 실시간 세션 저장
    redis_client.hset('active_sessions', current_user.id, json.dumps(session_data))

    # 모든 관리자에게 알림
    emit('focus_session_started', session_data, room='admin_dashboard')

    # 활동 로그 기록
    log_activity(current_user.id, 'focus_start', f"Started {data.get('duration')}min focus session")

@socketio.on('focus_session_end')
def handle_focus_end(data):
    """집중 세션 종료 이벤트"""
    session_data = {
        'user_id': current_user.id,
        'username': current_user.username,
        'end_time': datetime.utcnow().isoformat(),
        'productivity_score': data.get('productivity_score'),
        'interruptions': data.get('interruptions', 0)
    }

    # Redis에서 세션 제거
    redis_client.hdel('active_sessions', current_user.id)

    # 모든 관리자에게 알림
    emit('focus_session_ended', session_data, room='admin_dashboard')

    # 활동 로그 기록
    log_activity(current_user.id, 'focus_end', f"Completed focus session with score {data.get('productivity_score')}")
```

### **3단계: 관리자 대시보드**

#### **실시간 모니터링 대시보드**

```python
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """관리자 대시보드"""
    if current_user.role not in ['admin', 'manager']:
        return redirect(url_for('dashboard'))

    # 실시간 통계
    active_users = get_active_users_count()
    active_sessions = get_active_sessions()
    today_stats = get_today_statistics()
    weekly_trends = get_weekly_trends()

    return render_template('admin_dashboard.html',
                         active_users=active_users,
                         active_sessions=active_sessions,
                         today_stats=today_stats,
                         weekly_trends=weekly_trends)

def get_active_users_count():
    """현재 활성 사용자 수 반환"""
    # Redis에서 활성 세션 수 확인
    active_sessions = redis_client.hgetall('active_sessions')
    return len(active_sessions)

def get_active_sessions():
    """현재 활성 세션 목록 반환"""
    active_sessions = redis_client.hgetall('active_sessions')
    sessions = []

    for user_id, session_data in active_sessions.items():
        session_info = json.loads(session_data)
        user = User.query.get(int(user_id))
        if user:
            session_info['username'] = user.username
            session_info['department'] = user.department
            sessions.append(session_info)

    return sessions
```

---

## 👥 다중 사용자 관리 시스템

### **1단계: 사용자 권한 시스템**

#### **역할 기반 접근 제어 (RBAC)**

```python
class RoleBasedAccessControl:
    """역할 기반 접근 제어 시스템"""

    def __init__(self):
        self.roles = {
            'admin': {
                'permissions': [
                    'user_management',
                    'system_configuration',
                    'data_export',
                    'reports_generation',
                    'api_access'
                ],
                'description': '시스템 관리자 - 모든 권한'
            },
            'manager': {
                'permissions': [
                    'team_management',
                    'team_reports',
                    'user_monitoring',
                    'data_export'
                ],
                'description': '팀 매니저 - 팀 관리 권한'
            },
            'user': {
                'permissions': [
                    'personal_dashboard',
                    'personal_reports',
                    'focus_sessions'
                ],
                'description': '일반 사용자 - 개인 기능만'
            }
        }

    def has_permission(self, user, permission):
        """사용자가 특정 권한을 가지고 있는지 확인"""
        if not user or not user.is_active:
            return False

        user_role = user.role
        if user_role not in self.roles:
            return False

        return permission in self.roles[user_role]['permissions']

# 권한 데코레이터
def require_permission(permission):
    """권한 확인 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))

            rbac = RoleBasedAccessControl()
            if not rbac.has_permission(current_user, permission):
                return jsonify({'error': '권한이 없습니다'}), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator
```

### **2단계: 팀 관리 시스템**

#### **부서 및 팀 구조 관리**

```python
class Department(db.Model):
    """부서 모델"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 관계 설정
    users = db.relationship('User', backref='department_info', lazy=True)
    manager = db.relationship('User', foreign_keys=[manager_id])

class Team(db.Model):
    """팀 모델"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    leader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 관계 설정
    department = db.relationship('Department', backref='teams')
    leader = db.relationship('User', foreign_keys=[leader_id])
    members = db.relationship('User', secondary='team_members')

# 팀 멤버 관계 테이블
team_members = db.Table('team_members',
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('joined_at', db.DateTime, default=datetime.utcnow)
)

@app.route('/api/teams', methods=['POST'])
@login_required
@require_permission('team_management')
def create_team():
    """팀 생성 API"""
    data = request.get_json()

    team = Team(
        name=data['name'],
        department_id=data['department_id'],
        leader_id=data.get('leader_id'),
        description=data.get('description', '')
    )

    db.session.add(team)
    db.session.commit()

    # 팀 멤버 추가
    if 'member_ids' in data:
        for user_id in data['member_ids']:
            user = User.query.get(user_id)
            if user:
                team.members.append(user)

    db.session.commit()

    return jsonify({'success': True, 'team_id': team.id})
```

### **3단계: 사용자 활동 추적**

#### **실시간 사용자 활동 모니터링**

```python
class UserActivityTracker:
    """사용자 활동 추적 시스템"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def track_user_activity(self, user_id, activity_type, details=None):
        """사용자 활동 추적"""
        activity_data = {
            'user_id': user_id,
            'activity_type': activity_type,
            'timestamp': datetime.utcnow().isoformat(),
            'details': details or {},
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }

        # Redis에 실시간 활동 저장
        self.redis_client.lpush(f'user_activity:{user_id}', json.dumps(activity_data))
        self.redis_client.expire(f'user_activity:{user_id}', 86400)  # 24시간 보관

        # 전체 활동 스트림에 추가
        self.redis_client.lpush('global_activity_stream', json.dumps(activity_data))
        self.redis_client.ltrim('global_activity_stream', 0, 9999)  # 최근 10000개만 유지

        # 활동 로그 DB에 저장
        log_activity(user_id, activity_type, str(details))

    def get_user_activity(self, user_id, limit=50):
        """사용자 활동 기록 조회"""
        activities = self.redis_client.lrange(f'user_activity:{user_id}', 0, limit-1)
        return [json.loads(activity) for activity in activities]

    def get_recent_activities(self, limit=100):
        """최근 전체 활동 조회"""
        activities = self.redis_client.lrange('global_activity_stream', 0, limit-1)
        return [json.loads(activity) for activity in activities]

# 활동 추적 인스턴스
activity_tracker = UserActivityTracker()
```

---

## 🔄 실시간 데이터 동기화

### **1단계: 클라이언트-서버 동기화**

#### **WebSocket 기반 실시간 동기화**

```python
class ClientStateManager:
    """클라이언트 상태 관리"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def update_client_state(self, user_id, state_data):
        """클라이언트 상태 업데이트"""
        state_data['last_updated'] = datetime.utcnow().isoformat()
        self.redis_client.hset('client_states', user_id, json.dumps(state_data))

        # 관리자에게 상태 변경 알림
        socketio.emit('client_state_updated', {
            'user_id': user_id,
            'state': state_data
        }, room='admin_dashboard')

    def get_client_state(self, user_id):
        """클라이언트 상태 조회"""
        state_data = self.redis_client.hget('client_states', user_id)
        return json.loads(state_data) if state_data else None

    def get_all_client_states(self):
        """모든 클라이언트 상태 조회"""
        states = self.redis_client.hgetall('client_states')
        return {user_id: json.loads(state) for user_id, state in states.items()}

client_state_manager = ClientStateManager()

@socketio.on('client_state_update')
def handle_client_state_update(data):
    """클라이언트 상태 업데이트 처리"""
    if current_user.is_authenticated:
        client_state_manager.update_client_state(current_user.id, data)
```

### **2단계: 데이터베이스 동기화**

#### **비동기 데이터 동기화 시스템**

```python
class DataSyncManager:
    """데이터 동기화 관리자"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.sync_queue = queue.Queue()
        self.start_sync_workers()

    def start_sync_workers(self):
        """동기화 워커 스레드 시작"""
        for i in range(3):  # 3개의 워커 스레드
            worker = threading.Thread(target=self._sync_worker, args=(i,), daemon=True)
            worker.start()

    def _sync_worker(self, worker_id):
        """동기화 워커 루프"""
        while True:
            try:
                # 동기화 작업 대기
                sync_task = self.sync_queue.get(timeout=1)
                self._process_sync_task(sync_task)
                self.sync_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"동기화 워커 {worker_id} 오류: {e}")

    def _process_sync_task(self, task):
        """동기화 작업 처리"""
        task_type = task.get('type')

        if task_type == 'focus_session':
            self._sync_focus_session(task['data'])
        elif task_type == 'user_activity':
            self._sync_user_activity(task['data'])
        elif task_type == 'user_profile':
            self._sync_user_profile(task['data'])

    def _sync_focus_session(self, session_data):
        """집중 세션 동기화"""
        try:
            # 중복 확인
            existing_session = FocusSession.query.filter_by(
                user_id=session_data['user_id'],
                start_time=datetime.fromisoformat(session_data['start_time'])
            ).first()

            if not existing_session:
                session = FocusSession(
                    user_id=session_data['user_id'],
                    start_time=datetime.fromisoformat(session_data['start_time']),
                    end_time=datetime.fromisoformat(session_data['end_time']) if session_data.get('end_time') else None,
                    duration=session_data.get('duration'),
                    status=session_data.get('status', 'active'),
                    problem_id=session_data.get('problem_id'),
                    productivity_score=session_data.get('productivity_score')
                )
                db.session.add(session)
                db.session.commit()

                print(f"집중 세션 동기화 완료: {session.id}")
        except Exception as e:
            print(f"집중 세션 동기화 실패: {e}")

    def queue_sync_task(self, task_type, data):
        """동기화 작업 큐에 추가"""
        task = {
            'type': task_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        self.sync_queue.put(task)

# 데이터 동기화 관리자 인스턴스
sync_manager = DataSyncManager()
```

---

## 📊 고급 통계 및 분석 시스템

### **1단계: 통계 데이터 모델**

#### **통계 데이터 구조**

```python
class StatisticsSnapshot(db.Model):
    """통계 스냅샷 모델"""
    id = db.Column(db.Integer, primary_key=True)
    snapshot_date = db.Column(db.Date, nullable=False)
    snapshot_type = db.Column(db.String(50))  # daily, weekly, monthly

    # 사용자 통계
    total_users = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    new_users = db.Column(db.Integer, default=0)

    # 집중 세션 통계
    total_sessions = db.Column(db.Integer, default=0)
    completed_sessions = db.Column(db.Integer, default=0)
    total_focus_time = db.Column(db.Integer, default=0)  # 분 단위
    avg_session_duration = db.Column(db.Float, default=0.0)
    avg_productivity_score = db.Column(db.Float, default=0.0)

    # 부서별 통계 (JSON 형태로 저장)
    department_stats = db.Column(db.Text)  # JSON string

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ProductivityMetrics(db.Model):
    """생산성 지표 모델"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)

    # 일일 생산성 지표
    total_focus_time = db.Column(db.Integer, default=0)  # 분 단위
    sessions_completed = db.Column(db.Integer, default=0)
    avg_productivity_score = db.Column(db.Float, default=0.0)
    interruptions = db.Column(db.Integer, default=0)
    problems_solved = db.Column(db.Integer, default=0)

    # 시간대별 생산성 (JSON 형태로 저장)
    hourly_productivity = db.Column(db.Text)  # JSON string

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### **2단계: 통계 계산 엔진**

#### **실시간 통계 계산**

```python
class StatisticsEngine:
    """통계 계산 엔진"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)

    def calculate_daily_statistics(self, date=None):
        """일일 통계 계산"""
        if date is None:
            date = datetime.utcnow().date()

        # 기본 통계 계산
        stats = {
            'date': date.isoformat(),
            'total_users': User.query.filter_by(is_active=True).count(),
            'active_users': self._get_active_users_count(date),
            'new_users': self._get_new_users_count(date),
            'total_sessions': self._get_total_sessions_count(date),
            'completed_sessions': self._get_completed_sessions_count(date),
            'total_focus_time': self._get_total_focus_time(date),
            'avg_session_duration': self._get_avg_session_duration(date),
            'avg_productivity_score': self._get_avg_productivity_score(date),
            'department_stats': self._get_department_stats(date)
        }

        # 스냅샷 저장
        self._save_statistics_snapshot(stats, 'daily')

        return stats

    def _get_active_users_count(self, date):
        """활성 사용자 수 계산"""
        return FocusSession.query.filter(
            db.func.date(FocusSession.start_time) == date
        ).distinct(FocusSession.user_id).count()

    def _get_total_sessions_count(self, date):
        """총 세션 수 계산"""
        return FocusSession.query.filter(
            db.func.date(FocusSession.start_time) == date
        ).count()

    def _get_total_focus_time(self, date):
        """총 집중 시간 계산"""
        result = db.session.query(
            db.func.sum(FocusSession.duration)
        ).filter(
            db.func.date(FocusSession.start_time) == date
        ).scalar()
        return result or 0

    def _get_avg_productivity_score(self, date):
        """평균 생산성 점수 계산"""
        result = db.session.query(
            db.func.avg(FocusSession.productivity_score)
        ).filter(
            db.func.date(FocusSession.start_time) == date,
            FocusSession.productivity_score.isnot(None)
        ).scalar()
        return round(result or 0, 2)

    def _get_department_stats(self, date):
        """부서별 통계 계산"""
        departments = Department.query.all()
        dept_stats = {}

        for dept in departments:
            dept_users = User.query.filter_by(department_id=dept.id, is_active=True).all()
            user_ids = [user.id for user in dept_users]

            if user_ids:
                dept_sessions = FocusSession.query.filter(
                    FocusSession.user_id.in_(user_ids),
                    db.func.date(FocusSession.start_time) == date
                ).all()

                total_time = sum(session.duration or 0 for session in dept_sessions)
                avg_score = sum(session.productivity_score or 0 for session in dept_sessions) / len(dept_sessions) if dept_sessions else 0

                dept_stats[dept.name] = {
                    'total_sessions': len(dept_sessions),
                    'total_focus_time': total_time,
                    'avg_productivity_score': round(avg_score, 2),
                    'active_users': len(set(session.user_id for session in dept_sessions))
                }

        return dept_stats

    def _save_statistics_snapshot(self, stats, snapshot_type):
        """통계 스냅샷 저장"""
        snapshot = StatisticsSnapshot(
            snapshot_date=datetime.fromisoformat(stats['date']).date(),
            snapshot_type=snapshot_type,
            total_users=stats['total_users'],
            active_users=stats['active_users'],
            new_users=stats['new_users'],
            total_sessions=stats['total_sessions'],
            completed_sessions=stats['completed_sessions'],
            total_focus_time=stats['total_focus_time'],
            avg_session_duration=stats['avg_session_duration'],
            avg_productivity_score=stats['avg_productivity_score'],
            department_stats=json.dumps(stats['department_stats'])
        )

        db.session.add(snapshot)
        db.session.commit()

# 통계 엔진 인스턴스
stats_engine = StatisticsEngine()
```

### **3단계: 리포트 생성 시스템**

#### **PDF 리포트 생성**

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import io

class ReportGenerator:
    """리포트 생성기"""

    def __init__(self):
        self.styles = getSampleStyleSheet()

    def generate_daily_report(self, date, output_path=None):
        """일일 리포트 생성"""
        if output_path is None:
            output_path = f"reports/daily_report_{date.strftime('%Y%m%d')}.pdf"

        # 통계 데이터 조회
        stats = stats_engine.calculate_daily_statistics(date)

        # PDF 생성
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        story = []

        # 제목
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # 중앙 정렬
        )
        title = Paragraph(f"FocusTimer 일일 리포트 - {date.strftime('%Y년 %m월 %d일')}", title_style)
        story.append(title)
        story.append(Spacer(1, 20))

        # 요약 통계 테이블
        summary_data = [
            ['지표', '값'],
            ['총 사용자 수', str(stats['total_users'])],
            ['활성 사용자 수', str(stats['active_users'])],
            ['신규 사용자 수', str(stats['new_users'])],
            ['총 세션 수', str(stats['total_sessions'])],
            ['완료된 세션 수', str(stats['completed_sessions'])],
            ['총 집중 시간', f"{stats['total_focus_time']}분"],
            ['평균 세션 시간', f"{stats['avg_session_duration']}분"],
            ['평균 생산성 점수', str(stats['avg_productivity_score'])]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(summary_table)
        story.append(Spacer(1, 20))

        # 부서별 통계
        if stats['department_stats']:
            dept_title = Paragraph("부서별 통계", self.styles['Heading2'])
            story.append(dept_title)
            story.append(Spacer(1, 10))

            dept_data = [['부서', '세션 수', '집중 시간', '평균 생산성']]
            for dept_name, dept_stats in stats['department_stats'].items():
                dept_data.append([
                    dept_name,
                    str(dept_stats['total_sessions']),
                    f"{dept_stats['total_focus_time']}분",
                    str(dept_stats['avg_productivity_score'])
                ])

            dept_table = Table(dept_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch])
            dept_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))

            story.append(dept_table)

        # PDF 생성
        doc.build(story)
        return output_path

# 리포트 생성기 인스턴스
report_generator = ReportGenerator()

@app.route('/admin/reports/daily/<date>')
@login_required
@require_permission('reports_generation')
def download_daily_report(date):
    """일일 리포트 다운로드"""
    try:
        report_date = datetime.strptime(date, '%Y-%m-%d').date()
        report_path = report_generator.generate_daily_report(report_date)

        return send_file(report_path, as_attachment=True, download_name=f"daily_report_{date}.pdf")
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

## 🔌 API 통합 및 확장성

### **1단계: RESTful API 설계**

#### **API 엔드포인트 구조**

```python
# API 버전 관리
API_VERSION = 'v1'

# API 라우트 그룹
api_bp = Blueprint('api', __name__, url_prefix=f'/api/{API_VERSION}')

@api_bp.route('/users', methods=['GET'])
@login_required
@require_permission('user_management')
def get_users():
    """사용자 목록 조회 API"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    department = request.args.get('department')
    role = request.args.get('role')

    query = User.query.filter_by(is_active=True)

    if department:
        query = query.filter_by(department=department)
    if role:
        query = query.filter_by(role=role)

    users = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'users': [{
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'department': user.department,
            'last_login': user.last_login.isoformat() if user.last_login else None
        } for user in users.items],
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': users.total,
            'pages': users.pages
        }
    })

@api_bp.route('/users/<int:user_id>/stats', methods=['GET'])
@login_required
@require_permission('user_monitoring')
def get_user_stats(user_id):
    """사용자 통계 조회 API"""
    user = User.query.get_or_404(user_id)

    # 기간 설정
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = datetime.utcnow().date() - timedelta(days=30)

    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = datetime.utcnow().date()

    # 통계 계산
    sessions = FocusSession.query.filter(
        FocusSession.user_id == user_id,
        db.func.date(FocusSession.start_time).between(start_date, end_date)
    ).all()

    total_sessions = len(sessions)
    total_focus_time = sum(session.duration or 0 for session in sessions)
    avg_productivity = sum(session.productivity_score or 0 for session in sessions) / total_sessions if total_sessions > 0 else 0

    # 일별 통계
    daily_stats = {}
    for session in sessions:
        date = session.start_time.date()
        if date not in daily_stats:
            daily_stats[date] = {
                'sessions': 0,
                'focus_time': 0,
                'productivity_scores': []
            }

        daily_stats[date]['sessions'] += 1
        daily_stats[date]['focus_time'] += session.duration or 0
        if session.productivity_score:
            daily_stats[date]['productivity_scores'].append(session.productivity_score)

    # 일별 평균 생산성 계산
    for date in daily_stats:
        scores = daily_stats[date]['productivity_scores']
        daily_stats[date]['avg_productivity'] = sum(scores) / len(scores) if scores else 0
        del daily_stats[date]['productivity_scores']

    return jsonify({
        'user': {
            'id': user.id,
            'username': user.username,
            'department': user.department
        },
        'period': {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        },
        'summary': {
            'total_sessions': total_sessions,
            'total_focus_time': total_focus_time,
            'avg_productivity_score': round(avg_productivity, 2)
        },
        'daily_stats': {
            date.isoformat(): stats for date, stats in daily_stats.items()
        }
    })
```

### **2단계: 외부 시스템 연동**

#### **Slack 연동 시스템**

```python
import requests

class SlackIntegration:
    """Slack 연동 시스템"""

    def __init__(self, webhook_url):
        self.webhook_url = webhook_url

    def send_focus_session_notification(self, user, session_data):
        """집중 세션 알림 전송"""
        message = {
            "text": f"🎯 {user.username}님이 {session_data['duration']}분 집중 세션을 시작했습니다!",
            "attachments": [
                {
                    "color": "#36a64f",
                    "fields": [
                        {
                            "title": "사용자",
                            "value": user.username,
                            "short": True
                        },
                        {
                            "title": "부서",
                            "value": user.department or "미지정",
                            "short": True
                        },
                        {
                            "title": "세션 시간",
                            "value": f"{session_data['duration']}분",
                            "short": True
                        },
                        {
                            "title": "시작 시간",
                            "value": session_data['start_time'],
                            "short": True
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=message)
            response.raise_for_status()
            print(f"Slack 알림 전송 성공: {user.username}")
        except Exception as e:
            print(f"Slack 알림 전송 실패: {e}")

    def send_daily_summary(self, stats):
        """일일 요약 알림 전송"""
        message = {
            "text": "📊 FocusTimer 일일 요약",
            "attachments": [
                {
                    "color": "#ff6b6b",
                    "fields": [
                        {
                            "title": "활성 사용자",
                            "value": str(stats['active_users']),
                            "short": True
                        },
                        {
                            "title": "총 세션",
                            "value": str(stats['total_sessions']),
                            "short": True
                        },
                        {
                            "title": "총 집중 시간",
                            "value": f"{stats['total_focus_time']}분",
                            "short": True
                        },
                        {
                            "title": "평균 생산성",
                            "value": str(stats['avg_productivity_score']),
                            "short": True
                        }
                    ]
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=message)
            response.raise_for_status()
            print("일일 요약 Slack 알림 전송 성공")
        except Exception as e:
            print(f"일일 요약 Slack 알림 전송 실패: {e}")

# Slack 연동 인스턴스
slack_integration = SlackIntegration('YOUR_SLACK_WEBHOOK_URL')
```

---

## 🔒 보안 강화 및 권한 관리

### **1단계: 인증 및 세션 관리**

#### **JWT 기반 인증 시스템**

```python
import jwt
from functools import wraps

class JWTAuthManager:
    """JWT 인증 관리자"""

    def __init__(self, secret_key):
        self.secret_key = secret_key

    def generate_token(self, user):
        """JWT 토큰 생성"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')

    def verify_token(self, token):
        """JWT 토큰 검증"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def get_user_from_token(self, token):
        """토큰에서 사용자 정보 추출"""
        payload = self.verify_token(token)
        if payload:
            return User.query.get(payload['user_id'])
        return None

# JWT 인증 관리자 인스턴스
jwt_auth = JWTAuthManager(app.config['SECRET_KEY'])

def jwt_required(f):
    """JWT 토큰 필요 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '토큰이 필요합니다'}), 401

        if token.startswith('Bearer '):
            token = token[7:]

        user = jwt_auth.get_user_from_token(token)
        if not user:
            return jsonify({'error': '유효하지 않은 토큰입니다'}), 401

        if not user.is_active:
            return jsonify({'error': '비활성화된 사용자입니다'}), 403

        return f(*args, **kwargs)
    return decorated_function
```

### **2단계: 데이터 암호화**

#### **민감 데이터 암호화**

```python
from cryptography.fernet import Fernet
import base64

class DataEncryption:
    """데이터 암호화 시스템"""

    def __init__(self, key=None):
        if key is None:
            self.key = Fernet.generate_key()
        else:
            self.key = key
        self.cipher = Fernet(self.key)

    def encrypt_data(self, data):
        """데이터 암호화"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return self.cipher.encrypt(data)

    def decrypt_data(self, encrypted_data):
        """데이터 복호화"""
        decrypted = self.cipher.decrypt(encrypted_data)
        return decrypted.decode('utf-8')

    def get_key(self):
        """암호화 키 반환"""
        return base64.urlsafe_b64encode(self.key).decode('utf-8')

# 데이터 암호화 인스턴스
data_encryption = DataEncryption()

class EncryptedUser(db.Model):
    """암호화된 사용자 정보 모델"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    encrypted_email = db.Column(db.LargeBinary)  # 암호화된 이메일
    encrypted_phone = db.Column(db.LargeBinary)  # 암호화된 전화번호
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_email(self, email):
        """이메일 암호화 저장"""
        self.encrypted_email = data_encryption.encrypt_data(email)

    def get_email(self):
        """이메일 복호화 반환"""
        if self.encrypted_email:
            return data_encryption.decrypt_data(self.encrypted_email)
        return None

    def set_phone(self, phone):
        """전화번호 암호화 저장"""
        self.encrypted_phone = data_encryption.encrypt_data(phone)

    def get_phone(self):
        """전화번호 복호화 반환"""
        if self.encrypted_phone:
            return data_encryption.decrypt_data(self.encrypted_phone)
        return None
```

### **3단계: API 보안 강화**

#### **Rate Limiting 및 DDoS 방지**

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Rate Limiting 설정
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/v1/users', methods=['GET'])
@limiter.limit("10 per minute")
@jwt_required
@require_permission('user_management')
def get_users():
    """사용자 목록 조회 API (Rate Limited)"""
    # ... 기존 코드 ...

@app.route('/api/v1/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    """로그인 API (Rate Limited)"""
    data = request.get_json()

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        token = jwt_auth.generate_token(user)
        return jsonify({'token': token, 'user': {
            'id': user.id,
            'username': user.username,
            'role': user.role
        }})

    return jsonify({'error': '잘못된 인증 정보'}), 401
```

---

## 🎯 핵심 기술적 성과

### **1. 엔터프라이즈급 아키텍처**

- ✅ **Flask + SQLAlchemy**: 확장 가능한 웹 프레임워크
- ✅ **Redis**: 실시간 데이터 캐싱 및 세션 관리
- ✅ **WebSocket**: 실시간 양방향 통신
- ✅ **JWT**: 안전한 API 인증

### **2. 다중 사용자 관리**

- ✅ **RBAC**: 역할 기반 접근 제어
- ✅ **부서/팀 구조**: 조직 계층 관리
- ✅ **실시간 모니터링**: 사용자 활동 추적
- ✅ **권한 관리**: 세밀한 접근 제어

### **3. 고급 통계 및 분석**

- ✅ **실시간 통계**: WebSocket 기반 실시간 업데이트
- ✅ **PDF 리포트**: 자동화된 리포트 생성
- ✅ **트렌드 분석**: 시계열 데이터 분석
- ✅ **부서별 성과**: 조직 단위 분석

### **4. API 통합 및 확장성**

- ✅ **RESTful API**: 표준화된 API 설계
- ✅ **Slack 연동**: 외부 시스템 통합
- ✅ **Rate Limiting**: API 보안 강화
- ✅ **버전 관리**: API 버전 호환성

### **5. 보안 강화**

- ✅ **JWT 인증**: 토큰 기반 인증
- ✅ **데이터 암호화**: 민감 정보 보호
- ✅ **권한 검증**: 세밀한 접근 제어
- ✅ **DDoS 방지**: Rate Limiting

---

## 💡 개발 과정에서의 교훈

### **1. 엔터프라이즈 개발의 복잡성**

- **다중 사용자 지원**: 단일 사용자에서 수백 명 지원으로의 확장
- **실시간 처리**: WebSocket과 Redis를 활용한 실시간 시스템
- **보안 요구사항**: 기업급 보안 및 권한 관리의 중요성

### **2. 확장성 고려사항**

- **데이터베이스 최적화**: 대용량 데이터 처리 최적화
- **캐싱 전략**: Redis를 활용한 성능 향상
- **API 설계**: RESTful API와 버전 관리의 중요성

### **3. 사용자 경험 우선**

- **실시간 피드백**: 사용자 활동의 즉시 반영
- **직관적 인터페이스**: 관리자와 일반 사용자 모두를 위한 UI
- **자동화**: 리포트 생성 및 알림 시스템

---

## 🎯 결론 및 다음 편 예고

개인용 FocusTimer에서 엔터프라이즈급 시스템으로의 확장을 통해, 조직 전체의 생산성 관리가 가능한 완전한 솔루션을 개발했습니다. 이번 개발 과정에서:

- **웹 기반 아키텍처**: Flask와 WebSocket을 활용한 실시간 시스템
- **다중 사용자 관리**: RBAC 기반의 세밀한 권한 관리
- **고급 통계**: 실시간 분석 및 자동화된 리포트 생성
- **API 통합**: 외부 시스템과의 원활한 연동
- **보안 강화**: 기업급 보안 및 데이터 보호

이제 FocusTimer는 개인 사용자부터 대규모 조직까지 모든 규모에서 사용할 수 있는 완전한 생산성 관리 플랫폼이 되었습니다! 🚀

---

## 📚 다음 편 예고

### **Part 3: 알고리즘 시스템 통합기**

- **알고리즘 탭**: GUI에 완전히 통합된 알고리즘 문제 시스템
- **실시간 문제 제공**: LeetCode, CodeForces 연동
- **진행도 추적**: 사용자의 문제 풀이 진행도 관리
- **학습 경로**: 개인화된 알고리즘 학습 경로 제공
- **성과 분석**: 문제 풀이 통계 및 성과 분석

### **Part 4: 성능 최적화 및 확장성**

- **메모리 최적화**: 대용량 데이터 처리 최적화
- **데이터베이스 최적화**: SQLite 성능 튜닝
- **백그라운드 작업**: 비동기 작업 처리 시스템
- **크로스 플랫폼**: Windows, Linux 지원 확장
- **모바일 연동**: iOS, Android 앱 개발

### **Part 5: AI 통합 및 미래 계획**

- **머신러닝**: 사용 패턴 학습 및 예측
- **개인화**: AI 기반 개인화된 추천 시스템
- **자동화**: AI 기반 자동 최적화
- **클라우드 서비스**: SaaS 모델로의 확장

---

**#FocusTimer #엔터프라이즈 #웹개발 #Flask #WebSocket #Redis #JWT #API #보안 #통계분석**
