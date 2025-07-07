// src/LearnPage.jsx
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./LearnPage.css";

function LearnPage() {
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchWords = async () => {
      try {
        const res = await fetch("/vocabulary/?user_id=anonymous&limit=10");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        setWords(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchWords();
  }, []);

  if (loading) {
    return <div className="LearnPage">Loading vocabulary…</div>;
  }
  if (error) {
    return <div className="LearnPage">Error: {error}</div>;
  }

  return (
    <div className="LearnPage">
      <h1>📚 Māori Vocabulary Learning</h1>
      <p>Here are some Māori words and their English meanings:</p>
      <ul>
        {words.map((w) => (
          <li key={w.id}>
            <strong>{w.maori}</strong>: {w.english}
          </li>
        ))}
      </ul>

      {/* 操作按钮组 */}
      <section className="button-group">
        <Link to="/">
          <button>🎯 Start Quiz</button>
        </Link>
        <Link to="/profile">
          <button>👤 Profile</button>
        </Link>
      </section>
    </div>
  );
}

export default LearnPage;