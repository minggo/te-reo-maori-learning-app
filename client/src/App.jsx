/* src/App.jsx */
import React, { useEffect, useState, useRef } from 'react';
import { Link } from 'react-router-dom';
import './App.css';

function App() {
  const [questions, setQuestions] = useState([]);
  const [current, setCurrent] = useState(0);
  const [choices, setChoices] = useState([]);
  const [selected, setSelected] = useState('');
  const [score, setScore] = useState(0);
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [timer, setTimer] = useState(20);
  const [finished, setFinished] = useState(false);
  const timerRef = useRef(null);

  // 拉取题目
  useEffect(() => {
    async function fetchAll() {
      try {
        const res = await fetch('/quiz/?user_id=anonymous&limit=10');
        const data = await res.json();
        const list = Array.isArray(data) ? data : [data];
        setQuestions(list);
      } catch (e) {
        console.error(e);
      }
    }
    fetchAll();
  }, []);

  // 切换题目时初始化
  useEffect(() => {
    if (questions.length === 0) return;
    const q = questions[current];
    setChoices(shuffleArray(q.options));
    setSelected('');
    setShowFeedback(false);
    setFeedback('');
    setTimer(20);
    clearInterval(timerRef.current);
  }, [current, questions]);

  // 倒计时逻辑
  useEffect(() => {
    if (questions.length === 0 || showFeedback || finished) return;
    timerRef.current = setInterval(() => {
      setTimer(prev => prev - 1);
    }, 1000);
    return () => clearInterval(timerRef.current);
  }, [showFeedback, finished, questions]);

  // 时间结束处理: 自动挪到下一题
  useEffect(() => {
    if (timer <= 0 && !showFeedback && questions.length > 0) {
      clearInterval(timerRef.current);
      const correct = questions[current].answer;
      setShowFeedback(true);
      setFeedback(`⏰ Time's up! Answer: ${correct}`);
      recordStats(false);
      setTimeout(() => {
        if (current + 1 < questions.length) {
          setCurrent(prev => prev + 1);
        } else {
          setFinished(true);
        }
      }, 1000);
    }
  }, [timer, showFeedback, questions, current]);

  const recordStats = (isCorrect) => {
    const stats = JSON.parse(localStorage.getItem('quizStats') || '{"total":0,"correct":0}');
    stats.total += 1;
    if (isCorrect) stats.correct += 1;
    localStorage.setItem('quizStats', JSON.stringify(stats));
  };

  const handleSelect = (choice) => {
    if (showFeedback) return;
    clearInterval(timerRef.current);
    setSelected(choice);
    setShowFeedback(true);
    const correct = questions[current].answer;
    const isCorrect = choice === correct;
    if (isCorrect) {
      setScore(prev => prev + 1);
      setFeedback('✅ Correct!');
    } else {
      setFeedback(`❌ Wrong! Answer: ${correct}`);
    }
    recordStats(isCorrect);
  };

  const nextQuestion = () => {
    if (current + 1 < questions.length) {
      setCurrent(prev => prev + 1);
    } else {
      setFinished(true);
    }
  };

  if (questions.length === 0) {
    return <div className="App">Loading quiz...</div>;
  }

  if (finished) {
    const total = questions.length;
    const errors = total - score;
    const errorRate = ((errors / total) * 100).toFixed(1);
    return (
      <div className="App">
        <div className="results-card">
          <h1>🎉 Quiz Complete!</h1>
          <p>Your Score: {score}/{total}</p>
          <p>Error Rate: {errorRate}%</p>
          <button onClick={() => window.location.reload()} className="btn btn-restart">
            Restart Quiz
          </button>
        </div>
      </div>
    );
  }

  const q = questions[current];
  return (
    <div className="App">
      <header className="app-header">
        <Link to="/learn" className="btn btn-learn">Learn Vocabulary</Link>
        <Link to="/profile" className="btn btn-profile">Profile</Link>
      </header>
      <div className="quiz-card">
        <div className="quiz-header">
          <h1>🌿 Māori Quiz</h1>
          <div className="progress">{current + 1}/{questions.length}</div>
        </div>
        <div className="timer">Time Left: {timer}s</div>
        <h2 className="maori-word">{q.maori}</h2>
        <div className="choices">
          {choices.map(c => (
            <button
              key={c}
              className={`choice ${selected === c ? 'selected' : ''}`}
              onClick={() => handleSelect(c)}
              disabled={showFeedback}
            >{c}</button>
          ))}
        </div>
        {showFeedback && (
          <div className="feedback">
            <p>{feedback}</p>
            <button onClick={nextQuestion} className="btn btn-next">
              {current + 1 < questions.length ? 'Next' : 'Finish'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// 工具函数：打乱数组
function shuffleArray(array) {
  return [...array].sort(() => Math.random() - 0.5);
}

export default App;
