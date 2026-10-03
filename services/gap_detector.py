from typing import List, Dict, Any
from collections import defaultdict


# Predefined taxonomy of skill areas and concepts
SKILL_TAXONOMY = {
    "Python": [
        "mutable", "immutable", "list comprehension", "gil", "global interpreter lock",
        "multiprocessing", "decorator", "closure", "memory management", "garbage collection",
        "reference counting", "generator", "asyncio", "iterables", "pep 8"
    ],
    "SQL & Databases": [
        "where", "having", "group by", "window functions", "partition by", "row_number",
        "rank", "dense_rank", "star schema", "fact table", "dimension table", "olap",
        "oltp", "indexing", "n+1 problem", "eager loading", "explain analyze"
    ],
    "Machine Learning": [
        "supervised", "unsupervised", "linear regression", "random forest", "k-means",
        "pca", "bias", "variance", "tradeoff", "overfitting", "underfitting",
        "regularization", "cross-validation", "data drift", "concept drift"
    ],
    "NLP & Transformers": [
        "tf-idf", "term frequency", "inverse document frequency", "cosine similarity",
        "transformer", "self-attention", "multi-head", "query", "key", "value",
        "softmax", "scaled dot-product"
    ],
    "Data Analysis & Statistics": [
        "missing values", "imputation", "eda", "a/b testing", "statistical significance",
        "p-value", "hypothesis testing", "simpson's paradox", "confounding variable"
    ],
    "HR & Communication": [
        "stakeholders", "communication", "star method", "bug", "root cause",
        "disagreement", "code review", "collaboration", "continuous learning",
        "active listening", "consensus"
    ]
}


def classify_term_to_skill(term: str, default_topic: str = "General") -> str:
    """Finds which high-level skill area a keyword belongs to."""
    lower_term = term.lower()
    for skill, terms in SKILL_TAXONOMY.items():
        if any(t in lower_term or lower_term in t for t in terms):
            return skill
    
    # Fallback to question topic
    if "python" in default_topic.lower():
        return "Python"
    if "sql" in default_topic.lower() or "database" in default_topic.lower():
        return "SQL & Databases"
    if "ml" in default_topic.lower() or "machine" in default_topic.lower():
        return "Machine Learning"
    if "nlp" in default_topic.lower():
        return "NLP & Transformers"
    if "data" in default_topic.lower() or "stat" in default_topic.lower():
        return "Data Analysis & Statistics"
    if "hr" in default_topic.lower() or "behavior" in default_topic.lower() or "communication" in default_topic.lower():
        return "HR & Communication"

    return "General Engineering"


def analyze_interview_gaps(interview) -> Dict[str, Any]:
    """
    Analyzes an interview session's questions and candidate answers to generate:
    1. Demonstrated concepts (Strengths)
    2. Needs improvement concepts (Partial coverage)
    3. Priority critical gaps (Missing crucial concepts)
    4. Skill area scores (Radar breakdown)
    5. Actionable study recommendations
    """
    demonstrated = []
    needs_improvement = []
    priority_gaps = []

    skill_scores = defaultdict(lambda: {"total_score": 0.0, "count": 0, "demonstrated": set(), "missing": set()})

    for answer in interview.answers:
        q = answer.question
        score = answer.final_question_score or 0.0
        topic = getattr(q, "topic", q.role)
        skill_area = classify_term_to_skill(topic, default_topic=topic)

        feedback_dict = answer.get_feedback_dict()
        matched = answer.question.get_keywords_list()
        # If evaluator stored matched keywords
        if hasattr(answer, "_temp_matched"):
            matched_kws = answer._temp_matched
            missing_kws = answer._temp_missing
        else:
            # Reconstruct or parse from feedback
            kws = q.get_keywords_list()
            ans_text = (answer.answer_text or "").lower()
            matched_kws = [k for k in kws if k.lower() in ans_text]
            missing_kws = [k for k in kws if k.lower() not in ans_text]

        skill_scores[skill_area]["total_score"] += score
        skill_scores[skill_area]["count"] += 1
        skill_scores[skill_area]["demonstrated"].update(matched_kws)
        skill_scores[skill_area]["missing"].update(missing_kws)

        # Categorize by score threshold
        if score >= 75:
            for kw in matched_kws:
                demonstrated.append({
                    "concept": kw,
                    "skill_area": skill_area,
                    "question": q.question,
                    "score": score
                })
        elif score >= 40:
            for kw in matched_kws:
                demonstrated.append({
                    "concept": kw,
                    "skill_area": skill_area,
                    "question": q.question,
                    "score": score
                })
            for kw in missing_kws:
                needs_improvement.append({
                    "concept": kw,
                    "skill_area": skill_area,
                    "question": q.question,
                    "score": score
                })
        else:
            for kw in missing_kws:
                priority_gaps.append({
                    "concept": kw,
                    "skill_area": skill_area,
                    "question": q.question,
                    "score": score
                })

    # Calculate skill proficiency map
    skill_breakdown = {}
    for skill, data in skill_scores.items():
        avg = round(data["total_score"] / max(1, data["count"]), 1)
        skill_breakdown[skill] = {
            "score": avg,
            "demonstrated_count": len(data["demonstrated"]),
            "missing_count": len(data["missing"]),
            "status": "Proficient" if avg >= 75 else ("Developing" if avg >= 50 else "Needs Focus")
        }

    # Generate targeted study recommendations
    recommendations = []
    seen_skills = set()
    for gap in priority_gaps[:6]:
        skill = gap["skill_area"]
        if skill not in seen_skills:
            seen_skills.add(skill)
            recommendations.append({
                "skill_area": skill,
                "focus_concept": gap["concept"],
                "recommendation": f"Review core principles of '{gap['concept']}' in {skill}. Practice explaining trade-offs and code examples.",
                "priority": "High"
            })

    for gap in needs_improvement[:4]:
        skill = gap["skill_area"]
        if skill not in seen_skills and len(recommendations) < 6:
            seen_skills.add(skill)
            recommendations.append({
                "skill_area": skill,
                "focus_concept": gap["concept"],
                "recommendation": f"Deepen your familiarity with '{gap['concept']}' in {skill} by writing hands-on code or system designs.",
                "priority": "Medium"
            })

    if not recommendations:
        recommendations.append({
            "skill_area": "Overall Readiness",
            "focus_concept": "Advanced System Design & Scalability",
            "recommendation": "Great job! Keep testing yourself on Hard difficulty questions to maintain peak interview fluency.",
            "priority": "Low"
        })

    return {
        "demonstrated": demonstrated,
        "needs_improvement": needs_improvement,
        "priority_gaps": priority_gaps,
        "skill_breakdown": skill_breakdown,
        "recommendations": recommendations,
        "total_demonstrated_count": len(demonstrated),
        "total_gaps_count": len(priority_gaps) + len(needs_improvement),
    }


def aggregate_historical_gaps(interviews) -> Dict[str, Any]:
    """
    Aggregates skill performance across all interviews for candidate dashboard analytics.
    """
    skill_totals = defaultdict(lambda: {"total": 0.0, "count": 0})
    for itw in interviews:
        if not itw.is_completed:
            continue
        gaps = analyze_interview_gaps(itw)
        for skill, info in gaps.get("skill_breakdown", {}).items():
            skill_totals[skill]["total"] += info["score"]
            skill_totals[skill]["count"] += 1

    chart_labels = []
    chart_values = []
    for skill, data in skill_totals.items():
        chart_labels.append(skill)
        chart_values.append(round(data["total"] / max(1, data["count"]), 1))

    return {
        "labels": chart_labels,
        "values": chart_values
    }
