// src/LearnPage.jsx
import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import "./LearnPage.css";

function LearnPage() {
  // 从 localStorage 中读取已登录用户的 user_id（fallback 为 anonymous）
  const userId = localStorage.getItem("user_id") || "anonymous";
  
  const [words, setWords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 抽取 fetch 函数，便于重复调用
  const fetchWords = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log("Fetching words for user_id", userId);
      const res = await fetch(`/vocabulary/?user_id=${userId}&limit=10`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setWords(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWords();
  }, [userId]);

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
        <button onClick={fetchWords} className="btn btn-next-words">
          🔄 Next Words
        </button>
        <Link to="/culture">
          <button className="btn btn-culture">🌐 Culture</button>
        </Link>
      </section>
    </div>
  );
}

export default LearnPage;