from pathlib import Path
import sys

from fastapi.testclient import TestClient


ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from app.main import app


client = TestClient(app)


PROBES = [
    {
        "name": "vague",
        "messages": [{"role": "user", "content": "I need an assessment"}],
    },
    {
        "name": "senior_java",
        "messages": [
            {
                "role": "user",
                "content": "Senior full-stack engineer with Core Java, Spring, SQL, AWS, and Docker.",
            }
        ],
    },
    {
        "name": "opq_gsa_compare",
        "messages": [{"role": "user", "content": "What is the difference between OPQ and GSA?"}],
    },
    {
        "name": "general_hiring_refusal",
        "messages": [{"role": "user", "content": "How should I interview candidates for culture fit?"}],
    },
    {
        "name": "remove_aws_add_personality",
        "messages": [
            {
                "role": "user",
                "content": "Senior backend engineer with Java, Spring, SQL, AWS, and Docker.",
            },
            {"role": "assistant", "content": "Here are SHL assessments."},
            {"role": "user", "content": "Remove AWS and add personality."},
        ],
    },
]


def main() -> None:
    failures = 0

    for probe in PROBES:
        response = client.post("/chat", json={"messages": probe["messages"]})
        data = response.json()
        names = [item["name"] for item in data["recommendations"]]
        ok = response.status_code == 200 and len(names) <= 10

        if not ok:
            failures += 1

        print(f"{probe['name']}: status={response.status_code} count={len(names)}")
        print(f"  reply={data.get('reply', '')[:120]}")
        print(f"  recommendations={names}")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
