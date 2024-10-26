import os
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import re

con = sqlite3.connect("db/vocabulary.db")
cur = con.cursor()

words = []
synonyms = []
collocations = []
texts = []
fillings = []

app = Flask(__name__)
app.config['SECRET_KEY'] = 'some_secret_key'
cur.execute("SELECT word_name, definition, synonyms, collocations, contextual, fill from vocabs ORDER BY RANDOM()")
for word_name, definition, synonym, collocation, contextual, fill in cur.fetchall():
    words.append({"word": word_name, "definition": definition})
    synonyms.append({"word": word_name, "synonyms": str(synonym).split(',')})
    collocations.append({"word": word_name, "collocations": collocation})
    texts.append({"word": word_name, "contextual": contextual})
    fillings.append({"word": word_name, "fill": fill})
cur.close()


@app.route('/')
@app.route('/main_page')
def main_page():
    return render_template('main.html')


@app.route('/choose_plan', methods=['GET', 'POST'])
def choose_plan():
    if request.method == 'POST':
        plan = request.form['plan']
        return redirect(url_for('study', plan=plan))
    return render_template('choose_plan.html')


@app.route('/study/<plan>', methods=["POST", "GET"])
def study(plan):
    plan_days = int(plan)
    if request.method == 'POST':
        day = request.form['day']
        return redirect(url_for('level1', day=day, plan=plan))
    return render_template('study.html', plan_days=plan_days)


@app.route('/level1/<plan>/<day>')
def level1(day, plan):
    day = int(day)
    plan_days = int(plan)

    words_per_day = len(words) // plan_days
    remainder = len(words) % plan_days

    start_idx = (day - 1) * words_per_day
    end_idx = start_idx + words_per_day

    if day == plan_days:
        end_idx += remainder

    day_words = words[start_idx:end_idx]
    day_synonyms = [syn for syn in synonyms if syn["word"] in [word["word"] for word in day_words]]

    return render_template('level1.html', plan=plan_days, day=day, words=day_words, synonyms=day_synonyms)


@app.route('/level2/<plan>/<day>')
def level2(day, plan):
    day = int(day)
    plan_days = int(plan)

    words_per_day = len(words) // plan_days
    remainder = len(words) % plan_days

    start_idx = (day - 1) * words_per_day
    end_idx = start_idx + words_per_day

    if day == plan_days:
        end_idx += remainder

    day_words = words[start_idx:end_idx]
    day_collocations = [col for col in collocations if col["word"] in [word["word"] for word in day_words]]
    return render_template('level2.html', plan=plan_days, day=day, words=day_words, collocations=day_collocations)


@app.route('/level3/<plan>/<day>')
def level3(day, plan):
    day = int(day)
    plan_days = int(plan)

    words_per_day = len(words) // plan_days
    remainder = len(words) % plan_days

    start_idx = (day - 1) * words_per_day
    end_idx = start_idx + words_per_day

    if day == plan_days:
        end_idx += remainder

    day_words = words[start_idx:end_idx]
    day_texts = [t for t in texts if t["word"] in [word["word"] for word in day_words]]

    combined_texts = []
    for i in range(0, len(day_texts), 3):
        word_names = [day_texts[j]["word"] for j in range(i, min(i + 3, len(day_texts)))]
        if len(day_texts[i:i + 3]) == 3:
            combined_text = " ".join(
                [day_texts[i]["contextual"], day_texts[i + 1]["contextual"], day_texts[i + 2]["contextual"]])
        else:
            combined_text = " ".join([text["contextual"] for text in day_texts[i:i + 3]])

        for word in word_names:
            combined_text = re.sub(rf"\b{re.escape(word)}\b".lower(), f"<strong>{word}</strong>".lower(), combined_text,
                                   flags=re.IGNORECASE)

        combined_texts.append({"words": ", ".join(word_names), "text": combined_text})

    return render_template('level3.html', plan=plan_days, day=day, combined_texts=combined_texts)


@app.route('/level4/<plan>/<day>', methods=["GET", "POST"])
def level4(day, plan):
    day = int(day)
    plan_days = int(plan)

    words_per_day = len(words) // plan_days
    remainder = len(words) % plan_days

    start_idx = (day - 1) * words_per_day
    end_idx = start_idx + words_per_day

    if day == plan_days:
        end_idx += remainder

    day_words = words[start_idx:end_idx]
    day_fillings = [i for i in fillings if i["word"] in [word["word"] for word in day_words]]

    if request.method == "POST":
        user_answers = []
        for idx, word in enumerate(day_words):
            user_answer = request.form.get(f'answer{idx + 1}')
            correct = user_answer.strip().lower() == word["word"].lower()
            user_answers.append({"word": word["word"], "user_answer": user_answer, "correct": correct})

        return render_template('level4_results.html', day=day, plan=plan, user_answers=user_answers)

    return render_template('level4.html', plan=plan, day=day, words=day_words, fillings=day_fillings)


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


if __name__ == '__main__':
    main()
