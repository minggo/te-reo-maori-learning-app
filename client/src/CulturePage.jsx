// src/CulturePage.jsx
import React from "react";
import { Link } from "react-router-dom";
import "./CulturePage.css";

export default function CulturePage() {
  const resources = [
    { title: "Te Ara: The Encyclopedia of New Zealand", url: "https://teara.govt.nz/en" },
    { title: "Māori Language Commission", url: "https://www.tetaurawhiri.govt.nz/" },
    { title: "New Zealand History - Māori Culture", url: "https://nzhistory.govt.nz/culture/maori" },
    { title: "Te Papa Collections Online", url: "https://collections.tepapa.govt.nz/" },
    { title: "Māori Culture on NZ History Online", url: "https://nzhistory.govt.nz/culture/maori" }
  ];

  return (
    <div className="CulturePage">
      <h1>🌿 Learn Māori Culture</h1>
      <p>Explore the richness of Māori heritage through these curated links:</p>
      <ul className="resource-list">
        {resources.map((r, i) => (
          <li key={i}>
            <a href={r.url} target="_blank" rel="noopener noreferrer">
              {r.title}
            </a>
          </li>
        ))}
      </ul>
      <Link to="/profile">
        <button>⬅ Back to Profile</button>
      </Link>
    </div>
  );
}
