import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./ProfilePage.css";

function ProfilePage() {
  const [viewedWords, setViewedWords] = useState([]);
  const [masteredWords, setMasteredWords] = useState([]);
  const [quizStats, setQuizStats] = useState({ total: 0, correct: 0 });
  const [leaders, setLeaders] = useState([]);

  useEffect(() => {
    setViewedWords(JSON.parse(localStorage.getItem("viewedWords") || "[]"));
    setMasteredWords(JSON.parse(localStorage.getItem("masteredWords") || "[]"));
    setQuizStats(JSON.parse(localStorage.getItem("quizStats") || "{ \"total\":0, \"correct\":0 }"));
    // fetch leaderboard
    fetch('http://localhost:8000/leaderboard')
      .then(res => res.json())
      .then(data => setLeaders(data))
      .catch(console.error);
  }, []);

  const accuracy = quizStats.total>0?((quizStats.correct/quizStats.total)*100).toFixed(1):"N/A";

  return (
    <div className="ProfilePage">
      <h1>👤 Personal Info</h1>
      <section className="section">
        <h2>Viewed Vocabulary</h2>
        {viewedWords.length===0? <p>No words viewed yet.</p>:
        <ul>{viewedWords.map((w,i)=><li key={i}><strong>{w.maori}</strong>: {w.english}</li>)}</ul>}
      </section>
      <section className="section">
        <h2>Mastered Vocabulary ✅</h2>
        {masteredWords.length===0? <p>No mastered words yet.</p>:
        <ul>{masteredWords.map((w,i)=><li key={i}><strong>{w.maori}</strong>: {w.english}</li>)}</ul>}
      </section>
      <section className="section">
        <h2>Quiz Stats</h2>
        <p>Total Attempts: {quizStats.total}</p>
        <p>Correct Answers: {quizStats.correct}</p>
        <p>Accuracy: {accuracy}%</p>
      </section>
      <section className="section">        
        <h2>Leaderboard 🏆</h2>
        {leaders.length===0 ? <p>Loading leaderboard...</p> : (
          <ol>{leaders.map(u=><li key={u.id}>{u.username} — {u.mastered_count} words</li>)}</ol>
        )}
      </section>
      <Link to="/">
        <button>⬅ Back to Quiz</button>
      </Link>
    </div>
  );
}

export default ProfilePage;
