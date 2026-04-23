from flask import Flask, jsonify, redirect, render_template, request, url_for

from database import (
    add_lab,
    add_student,
    add_submission,
    check_submission,
    get_labs,
    get_stats,
    get_students,
    get_submissions,
    init_db,
    request_revision,
    seed_demo_data,
)


app = Flask(__name__)
init_db()
seed_demo_data()


@app.get("/")
def index():
    status = request.args.get("status", "").strip()
    group_name = request.args.get("group", "").strip()
    return render_template(
        "index.html",
        students=get_students(),
        labs=get_labs(),
        submissions=get_submissions(status or None, group_name or None),
        stats=get_stats(),
        selected_status=status,
        group_name=group_name,
    )


@app.post("/students")
def create_student():
    add_student(request.form["full_name"].strip(), request.form["group_name"].strip())
    return redirect(url_for("index"))


@app.post("/labs")
def create_lab():
    add_lab(
        request.form["title"].strip(),
        request.form["subject"].strip(),
        int(request.form.get("max_score") or 5),
        request.form["deadline"].strip(),
    )
    return redirect(url_for("index"))


@app.post("/submissions")
def create_submission():
    add_submission(
        int(request.form["student_id"]),
        int(request.form["lab_work_id"]),
        request.form.get("comment", "").strip(),
    )
    return redirect(url_for("index"))


@app.post("/submissions/<int:submission_id>/check")
def check(submission_id):
    check_submission(
        submission_id,
        int(request.form.get("score") or 0),
        request.form.get("comment", "Работа проверена").strip(),
    )
    return redirect(url_for("index"))


@app.post("/submissions/<int:submission_id>/revision")
def revision(submission_id):
    request_revision(submission_id, request.form.get("comment", "Нужна доработка").strip())
    return redirect(url_for("index"))


@app.get("/api/submissions")
def api_submissions():
    status = request.args.get("status", "").strip()
    group_name = request.args.get("group", "").strip()
    submissions = get_submissions(status or None, group_name or None)
    return jsonify({"count": len(submissions), "items": submissions})


if __name__ == "__main__":
    app.run(debug=True)
