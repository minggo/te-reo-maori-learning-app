// src/RegisterPage.jsx
import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./RegisterPage.css";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [code, setCode] = useState("");
  const [step, setStep] = useState("form"); // "form" or "verify"
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError("");
    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }
    try {
      const res = await fetch(
        "/auth/register",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, email, password }),
        }
      );
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || JSON.stringify(data));
      }
      setSuccess("Registration successful! Verification code sent to email.");
      setStep("verify");
    } catch (err) {
      setError(err.message || "Registration failed.");
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await fetch(
        "/auth/verify",
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, code }),
        }
      );
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || JSON.stringify(data));
      }
      setSuccess("Verification successful! Redirecting to login...");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.message || "Verification failed.");
    }
  };

  return (
    <div className="RegisterPage">
      <div className="register-card">
        {step === "form" && (
          <>
            <h1>📝 Create Account</h1>
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleRegister} className="register-form">
              <label htmlFor="username">Username</label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
              />
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
              />
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
              />
              <button type="submit" className="btn btn-register">Register</button>
            </form>
            <div className="bottom-link">
              <Link to="/login">Already have an account? Login</Link>
            </div>
          </>
        )}
        {step === "verify" && (
          <>
            <h1>✉️ Verify Account</h1>
            {success && <div className="success-message">{success}</div>}
            {error && <div className="error-message">{error}</div>}
            <form onSubmit={handleVerify} className="register-form">
              <label htmlFor="code">Verification Code</label>
              <input
                id="code"
                type="text"
                value={code}
                onChange={e => setCode(e.target.value)}
                required
              />
              <button type="submit" className="btn btn-register">Verify</button>
            </form>
          </>
        )}
      </div>
    </div>
  );
}
