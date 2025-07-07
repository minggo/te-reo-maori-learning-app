/* src/App.jsx */
import React, { useEffect, useState, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './App.css';

function App() {
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([]);
  const [current, setCurrent] = useState(0);
  const [choices, setChoices] = useState([]);
  const [selected, setSelected] = useState('');
  const [score, setScore] = useState(0);
  const [wrongWordIds, setWrongWordIds] = useState([]);           // ①
  const [feedback, setFeedback] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [timer, setTimer] = useState(20);
  const [finished, setFinished] = useState(false);
  const timerRef = useRef(null);

  // 拉取题目
  useEffect(() => {
    (async () => {
      try {
        const res = await fetch('/quiz/?user_id=anonymous&limit=10');
        const data = await res.json();
        setQuestions(Array.isArray(data) ? data : [data]);
      } catch (e) {
        console.error(e);
      }
    })();
  }, []);

  // 切换题目时初始化
  useEffect(() => {
    if (!questions.length) return;
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
    if (!questions.length || showFeedback || finished) return;
    timerRef.current = setInterval(() => setTimer(t => t - 1), 1000);
    return () => clearInterval(timerRef.current);
  }, [showFeedback, finished, questions]);

  // 时间结束处理
  useEffect(() => {
    if (timer <= 0 && !showFeedback && questions.length) {
      clearInterval(timerRef.current);
      const q = questions[current];
      setShowFeedback(true);
      setFeedback(`⏰ Time's up! Answer: ${q.answer}`);
      recordStats(false, q.id);                      // ②
      setTimeout(() => advanceOrFinish(), 1000);
    }
  }, [timer]);

  // 监听 finished，一旦完成，提交错题并跳转
  useEffect(() => {
    if (finished) {
      (async () => {
        try {
          await fetch('/quiz/feedback', {             // ③ 根据实际接口改路径
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user_id: 'anonymous',
              wrong_word_ids: wrongWordIds
            })
          });
        } catch (e) {
          console.error('Failed to submit feedback:', e);
        } finally {
          navigate('/profile');                      // ④
        }
      })();
    }
  }, [finished]);

  // 记录统计及错题
  const recordStats = (isCorrect, wordId) => {
    const stats = JSON.parse(localStorage.getItem('quizStats') 
      || '{"total":0,"correct":0}');
    stats.total += 1;
    if (isCorrect) {
      stats.correct += 1;
      setScore(s => s + 1);
    } else {
      setWrongWordIds(ids => [...ids, wordId]);    // ⑤
    }
    localStorage.setItem('quizStats', JSON.stringify(stats));
  };

  const handleSelect = (choice) => {
    if (showFeedback) return;
    clearInterval(timerRef.current);
    setSelected(choice);
    setShowFeedback(true);
    const q = questions[current];
    const isCorrect = choice === q.answer;
    setFeedback(isCorrect ? '✅ Correct!' : `❌ Wrong! Answer: ${q.answer}`);
    recordStats(isCorrect, q.id);                   // ⑥
  };

  const advanceOrFinish = () => {
    if (current + 1 < questions.length) {
      setCurrent(c => c + 1);
    } else {
      setFinished(true);
    }
  };

  if (!questions.length) {
    return <div className="App">Loading quiz...</div>;
  }
  if (finished) {
    // 渲染空页面，useEffect 会处理提交并跳转
    return null;
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
            <button onClick={advanceOrFinish} className="btn btn-next">
              {current + 1 < questions.length ? 'Next' : 'Finish'}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

// 工具：打乱数组
function shuffleArray(array) {
  return [...array].sort(() => Math.random() - 0.5);
}

export default App;