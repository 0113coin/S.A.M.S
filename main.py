from core.models.announcer.announcer import Announcer
from core.models.announcer.event import Event
from core.models.announcer.news import Media
from core.models.config.generator import get_internal_params
from core.models.coach.coach import Coach
from core.models.main_model import main_model

if __name__ == "__main__":
    # 과거 사건 (있으면 전달)
    past_events: list[Event] = []

    # 1) 사건 N개 생성
    announcer = Announcer()
    new_events = announcer.generate_events(
        past_events=past_events,
        count=2,
        allowed_categories=["Tech", "Healthcare", "Policy"]
    )

    # 2) 언론사 목록
    outlets = [
        Media(name="뉴스24", bias=0.2, credibility=0.9),
        Media(name="SNS속보", bias=0.8, credibility=0.3),
    ]

    # 내부 파라미터 생성 및 코치 가중치 산출
    params = get_internal_params(seed=7)
    coach = Coach(params)
    weights = coach.adjust_weights()

    base_price = 100.0

    # 3) 각 사건에 대해 뉴스 생성 및 메인 모델 계산
    for ev in new_events:
        news_list = announcer.generate_news_for_event(ev, outlets, past_events=past_events)
        print("\n생성된 사건:", ev.event_type, "/", ev.category, "/", ev.duration)
        print("연결된 뉴스 ID:", ev.news_article)
        for n in news_list:
            print(f"\n언론사: {n.media}\n{n.article_text}")

        # 뉴스 임팩트 간단 추정: sentiment(-1~1)→[0,1] 변환 후 impact_level(1~5) 가중
        sentiment_score = max(0.0, min(1.0, (ev.sentiment + 1.0) / 2.0))
        impact_scale = max(0.0, min(1.0, ev.impact_level / 5.0))
        news_impact = round(sentiment_score * impact_scale, 3)

        # 메인 모델 계산
        result = main_model(weights, params, {"news_impact": news_impact}, base_price=base_price)
        print("\n🧮 메인 모델 계산:")
        print(f"- 가중치: {weights}")
        print(f"- 추정 news_impact: {news_impact}")
        print(f"- delta: {result['delta']}, price: {result['price']}")

        # 과거 목록에 이번 사건 추가 (다음 라운드 맥락 강화를 위해)
        past_events.append(ev)
