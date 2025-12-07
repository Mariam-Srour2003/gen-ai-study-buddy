"""Cute pastel single-page UI served from FastAPI - Vanilla HTML/CSS/JS."""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


ui_router = APIRouter()


APP_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Study Buddy - Chat with Your Docs</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&family=Rubik:wght@500;600;700;800&display=swap" rel="stylesheet" />
  <style>
    * { box-sizing: border-box; }
    
    body {
      margin: 0;
      font-family: 'Nunito', system-ui, -apple-system, sans-serif;
      background: linear-gradient(135deg, #fff5f9 0%, #f0f9ff 50%, #f0fff4 100%);
      color: #2d2a32;
      height: 100vh;
      overflow: hidden;
    }

    .container {
      display: flex;
      height: 100vh;
      gap: 0;
    }

    /* ===== SIDEBAR ===== */
    .sidebar {
      width: 320px;
      background: rgba(255, 255, 255, 0.6);
      backdrop-filter: blur(10px);
      border-right: 4px solid #ffc1e3;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .sidebar-header {
      padding: 24px;
      border-bottom: 4px solid #ffc1e3;
      background: linear-gradient(135deg, rgba(255, 193, 227, 0.15), rgba(199, 210, 254, 0.15));
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }

    .brand-logo {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: linear-gradient(135deg, #ff9ecb, #c7d2fe, #7dd3fc);
      display: grid;
      place-items: center;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
      font-size: 22px;
    }

    .brand-text h1 {
      margin: 0;
      font-size: 20px;
      font-weight: 800;
      background: linear-gradient(135deg, #ff6b9d 0%, #a78bfa 50%, #60a5fa 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      font-family: 'Rubik', sans-serif;
    }

    .brand-text p {
      margin: 4px 0 0 0;
      font-size: 12px;
      color: #6b6674;
    }

    .new-chat-btn {
      width: 100%;
      padding: 12px 16px;
      background: linear-gradient(135deg, #ff6b9d, #a78bfa);
      border: none;
      border-radius: 18px;
      color: white;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 6px 16px rgba(255, 107, 157, 0.3);
      transition: all 0.2s ease;
      font-family: 'Rubik', sans-serif;
    }

    .new-chat-btn:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 20px rgba(255, 107, 157, 0.4);
    }

    .sidebar-conversations {
      flex: 1;
      overflow-y: auto;
      padding: 16px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .conv-item {
      padding: 16px;
      background: white;
      border: 2px solid #fce7f3;
      border-radius: 18px;
      cursor: pointer;
      transition: all 0.2s ease;
      position: relative;
    }

    .conv-item:hover {
      background: #fdf2f8;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .conv-item.active {
      background: linear-gradient(135deg, #fce7f3, #e9d5ff);
      border-color: #ff6b9d;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }

    .conv-item.unread::before {
      content: '';
      position: absolute;
      top: 12px;
      right: 12px;
      width: 8px;
      height: 8px;
      background: #ff6b9d;
      border-radius: 50%;
    }

    .conv-title {
      font-weight: 700;
      font-size: 14px;
      color: #1f2937;
      margin-bottom: 4px;
      font-family: 'Rubik', sans-serif;
    }

    .conv-preview {
      font-size: 12px;
      color: #6b7280;
      margin-bottom: 4px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .conv-time {
      font-size: 11px;
      color: #9ca3af;
    }

    .sidebar-footer {
      padding: 16px 24px;
      border-top: 4px solid #ffc1e3;
      background: linear-gradient(135deg, #fef2f8, #faf5ff);
      font-size: 12px;
      color: #6b6674;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* ===== MAIN CHAT AREA ===== */
    .main {
      flex: 1;
      display: flex;
      flex-direction: column;
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.7), rgba(248, 240, 255, 0.5));
    }

    .header {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(10px);
      border-bottom: 4px solid #ffc1e3;
      padding: 24px;
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: 24px;
    }

    .header-left h2 {
      margin: 0 0 12px 0;
      font-size: 28px;
      font-weight: 700;
      color: #1f2937;
      font-family: 'Rubik', sans-serif;
    }

    .doc-pills {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 8px;
    }

    .doc-pill {
      padding: 8px 14px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
      border: 2px solid rgba(255, 255, 255, 0.8);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .doc-pill:hover {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    }

    .doc-pill-close {
      cursor: pointer;
      margin-left: 4px;
      opacity: 0.6;
    }

    .doc-pill-close:hover {
      opacity: 1;
    }

    .header-right {
      display: flex;
      gap: 12px;
    }

    .mode-btn {
      padding: 12px 18px;
      border-radius: 18px;
      border: none;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: all 0.2s ease;
      font-family: 'Rubik', sans-serif;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }

    .flashcard-btn {
      background: linear-gradient(135deg, #ff9ecb, #ff6b9d);
      color: white;
    }

    .quiz-btn {
      background: linear-gradient(135deg, #60a5fa, #a78bfa);
      color: white;
    }

    .mode-btn:hover {
      transform: translateY(-2px);
    }

    /* ===== MESSAGES AREA ===== */
    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 24px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    .message {
      display: flex;
      gap: 12px;
      animation: slideIn 0.3s ease-out;
    }

    .message.user {
      justify-content: flex-end;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .mascot {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      font-weight: bold;
      flex-shrink: 0;
      transition: all 0.3s ease;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }

    .mascot.happy {
      background: linear-gradient(135deg, rgba(255, 107, 157, 0.3), rgba(255, 107, 157, 0.1));
      border: 3px solid #ff6b9d;
      color: #ff6b9d;
    }

    .mascot.thinking {
      background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(167, 139, 250, 0.1));
      border: 3px solid #a78bfa;
      color: #a78bfa;
    }

    .mascot.excited {
      background: linear-gradient(135deg, rgba(251, 191, 36, 0.3), rgba(251, 191, 36, 0.1));
      border: 3px solid #fbbf24;
      color: #fbbf24;
      animation: bounce 0.6s ease-in-out infinite;
    }

    @keyframes bounce {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-4px); }
    }

    .bubble {
      max-width: 70%;
      padding: 16px 20px;
      border-radius: 24px;
      line-height: 1.5;
      word-wrap: break-word;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
      font-size: 14px;
    }

    .message.bot .bubble {
      background: white;
      color: #2d2a32;
      border: 3px solid #ffc1e3;
      border-top-left-radius: 4px;
      position: relative;
    }

    .message.bot .bubble::before {
      content: '✨';
      position: absolute;
      top: 4px;
      left: 8px;
      font-size: 10px;
      opacity: 0.4;
    }

    .message.user .bubble {
      background: linear-gradient(135deg, #ff6b9d, #ff9ecb);
      color: white;
      border-top-right-radius: 4px;
    }

    .message-time {
      font-size: 11px;
      color: #9ca3af;
      margin-top: 4px;
    }

    /* ===== CITATIONS ===== */
    .citations-container {
      max-width: 70%;
      margin-top: 12px;
      padding: 8px 12px;
      background: linear-gradient(135deg, rgba(199, 210, 254, 0.15), rgba(125, 211, 252, 0.15));
      border-left: 4px solid #a78bfa;
      border-radius: 12px;
      font-size: 13px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .citations-container:hover {
      background: linear-gradient(135deg, rgba(199, 210, 254, 0.25), rgba(125, 211, 252, 0.25));
    }

    .citations-title {
      font-weight: 700;
      color: #6b6674;
      display: flex;
      align-items: center;
      gap: 6px;
      user-select: none;
    }

    .citations-toggle {
      margin-left: auto;
      font-size: 12px;
      color: #a78bfa;
      transition: transform 0.2s ease;
    }

    .citations-container.collapsed .citations-toggle {
      transform: rotate(-90deg);
    }

    .citations-content {
      margin-top: 8px;
      max-height: 500px;
      overflow: hidden;
      transition: max-height 0.3s ease;
    }

    .citations-container.collapsed .citations-content {
      max-height: 0;
      margin-top: 0;
    }

    .citation-item {
      padding: 10px 12px;
      margin: 8px 0;
      background: rgba(255, 255, 255, 0.6);
      border-radius: 8px;
      border-left: 3px solid #c7d2fe;
      color: #4b5563;
      line-height: 1.5;
      font-size: 12px;
    }

    .citation-item strong {
      display: block;
      color: #a78bfa;
      font-weight: 700;
      margin-bottom: 4px;
    }

    .citation-score {
      display: inline-block;
      background: rgba(167, 139, 250, 0.2);
      color: #a78bfa;
      padding: 2px 6px;
      border-radius: 4px;
      font-size: 11px;
      font-weight: 600;
      margin-bottom: 6px;
    }

    .citation-text {
      color: #6b6674;
      font-size: 12px;
      line-height: 1.4;
      margin-top: 4px;
    }

    /* ===== INPUT AREA ===== */
    .input-area {
      background: rgba(255, 255, 255, 0.8);
      backdrop-filter: blur(10px);
      border-top: 4px solid #ffc1e3;
      padding: 20px 24px;
      display: flex;
      gap: 12px;
      align-items: flex-end;
    }

    .upload-btn {
      width: 48px;
      height: 48px;
      border-radius: 18px;
      background: linear-gradient(135deg, #a78bfa, #9f7aea);
      border: none;
      color: white;
      cursor: pointer;
      display: grid;
      place-items: center;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
      transition: all 0.2s ease;
      flex-shrink: 0;
    }

    .upload-btn:hover {
      transform: translateY(-2px);
    }

    .input-wrapper {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 12px;
      background: white;
      border-radius: 24px;
      border: 3px solid #ffc1e3;
      padding: 12px 16px;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    }

    .input-wrapper textarea {
      flex: 1;
      border: none;
      outline: none;
      font-family: 'Nunito', sans-serif;
      font-size: 14px;
      background: transparent;
      resize: none;
      min-height: 20px;
      max-height: 120px;
      overflow-y: auto;
      line-height: 1.5;
    }

    .input-wrapper textarea::placeholder {
      color: #9ca3af; /* higher contrast for visibility */
    }

    .mode-toggle {
      height: 44px;
      padding: 0 14px;
      border-radius: 14px;
      border: 2px solid #a78bfa;
      background: rgba(167, 139, 250, 0.12);
      color: #5b21b6;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      box-shadow: 0 4px 10px rgba(0, 0, 0, 0.08);
      transition: all 0.2s ease;
      flex-shrink: 0;
    }

    .mode-toggle:hover {
      transform: translateY(-1px);
      background: rgba(167, 139, 250, 0.2);
    }

    .send-btn {
      width: 48px;
      height: 48px;
      border-radius: 18px;
      background: linear-gradient(135deg, #ff6b9d, #ff9ecb);
      border: none;
      color: white;
      cursor: pointer;
      display: grid;
      place-items: center;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
      transition: all 0.2s ease;
      flex-shrink: 0;
    }

    .send-btn:hover {
      transform: translateY(-2px);
    }

    /* ===== PROVIDER HEADER ===== */
    .provider-selector {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.7);
      border-radius: 999px;
      border: 2px solid #ffc1e3;
    }

    .provider-selector label {
      font-size: 12px;
      font-weight: 600;
      color: #6b6674;
    }

    .provider-selector select {
      background: rgba(255, 193, 227, 0.2);
      border: none;
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      font-family: 'Rubik', sans-serif;
    }

    .provider-selector button {
      padding: 4px 10px;
      background: linear-gradient(135deg, #a8c5ff, #ffcfe9);
      border: none;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: 'Rubik', sans-serif;
    }

    .provider-selector button:hover {
      transform: scale(1.05);
    }

    /* ===== FLASHCARD & QUIZ CONTROLS ===== */
    .flashcard-control,
    .quiz-control {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: rgba(255, 255, 255, 0.7);
      border-radius: 999px;
      border: 2px solid #ffc1e3;
    }

    .flashcard-control label,
    .quiz-control label {
      font-size: 12px;
      font-weight: 600;
      color: #6b6674;
    }

    .flashcard-control select,
    .quiz-control select {
      background: rgba(255, 193, 227, 0.2);
      border: none;
      border-radius: 6px;
      padding: 4px 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      font-family: 'Rubik', sans-serif;
    }

    /* ===== MODAL ===== */
    .modal {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(4px);
      z-index: 1000;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }

    .modal.active {
      display: flex;
    }

    .modal-content {
      background: linear-gradient(135deg, #fff5f9, #f0f9ff, #f0fff4);
      border-radius: 32px;
      padding: 32px;
      max-width: 900px;
      width: 100%;
      max-height: 90vh;
      overflow-y: auto;
      box-shadow: 0 25px 70px rgba(0, 0, 0, 0.3);
      border: 4px solid #ffc1e3;
      position: relative;
    }

    .modal-close {
      position: absolute;
      top: 16px;
      right: 16px;
      width: 44px;
      height: 44px;
      background: white;
      border: none;
      border-radius: 50%;
      cursor: pointer;
      display: grid;
      place-items: center;
      font-size: 20px;
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }

    .modal-header {
      display: flex;
      align-items: center;
      gap: 24px;
      margin-bottom: 40px;
      padding-bottom: 24px;
      border-bottom: 2px solid #ffc1e3;
      min-height: 120px;
    }

    .modal-icon {
      width: 80px;
      height: 80px;
      min-width: 80px;
      min-height: 80px;
      max-width: 80px;
      max-height: 80px;
      border-radius: 50%;
      display: grid;
      place-items: center;
      font-size: 40px;
      box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
      flex-shrink: 0;
    }

    .modal-icon.flashcard {
      background: linear-gradient(135deg, #ff9ecb, #ff6b9d);
    }

    .modal-icon.quiz {
      background: linear-gradient(135deg, #60a5fa, #a78bfa);
    }

    .modal-header h2 {
      margin: 0 0 8px 0;
      font-size: 32px;
      font-weight: 800;
      font-family: 'Rubik', sans-serif;
      color: #1f2937;
    }

    .modal-header p {
      margin: 0;
      font-size: 15px;
      color: #6b6674;
      font-weight: 500;
    }

    /* ===== FLASHCARDS ===== */
    .flashcards-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 24px;
    }

    .flashcard {
      height: 240px;
      cursor: pointer;
      perspective: 1200px;
      position: relative;
    }

    .flashcard-inner {
      position: relative;
      width: 100%;
      height: 100%;
      transition: transform 0.6s;
      transform-style: preserve-3d;
    }

    .flashcard.flipped .flashcard-inner {
      transform: rotateY(180deg);
    }

    .flashcard-face {
      position: absolute;
      width: 100%;
      height: 100%;
      backface-visibility: hidden;
      border-radius: 28px;
      padding: 20px;
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
      border: 4px solid rgba(255, 255, 255, 0.8);
    }

    .flashcard-front {
      background: white;
      color: #2d2a32;
    }

    .flashcard-back {
      background: linear-gradient(135deg, #e9d5ff, #fce7f3, #d1fae5);
      color: #1f2937;
      transform: rotateY(180deg);
    }

    .flashcard-label {
      position: absolute;
      top: 12px;
      left: 12px;
      background: rgba(255, 107, 157, 0.2);
      color: #ff6b9d;
      padding: 4px 8px;
      border-radius: 6px;
      font-size: 11px;
      font-weight: 700;
    }

    /* ===== QUIZ ===== */
    .quiz-questions {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .quiz-question {
      background: white;
      border-radius: 28px;
      padding: 24px;
      box-shadow: 0 10px 30px rgba(96, 165, 250, 0.2);
      border: 4px solid #dbeafe;
      position: relative;
    }

    .question-num {
      position: absolute;
      top: -16px;
      right: 20px;
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, #60a5fa, #a78bfa);
      color: white;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-family: 'Rubik', sans-serif;
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }

    .question-text {
      font-size: 16px;
      font-weight: 600;
      color: #1f2937;
      margin-bottom: 16px;
      margin-top: 8px;
    }

    .options {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .option-btn {
      padding: 16px;
      border-radius: 18px;
      border: 3px solid #e5e7eb;
      background: white;
      text-align: left;
      cursor: pointer;
      transition: all 0.2s ease;
      font-family: 'Nunito', sans-serif;
      font-weight: 500;
    }

    .option-btn:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
    }

    .option-btn.correct {
      background: #d1fae5;
      border-color: #34d399;
    }

    .option-btn.wrong {
      background: #fee2e2;
      border-color: #f87171;
    }

    .option-btn.selected {
      background: #dbeafe;
      border-color: #60a5fa;
    }

    .modal-footer {
      margin-top: 32px;
      text-align: center;
      padding: 16px;
      background: white;
      border-radius: 18px;
      font-weight: 600;
      color: #a78bfa;
      font-family: 'Rubik', sans-serif;
    }

    ::-webkit-scrollbar {
      width: 8px;
    }

    ::-webkit-scrollbar-track {
      background: #fce7f3;
    }

    ::-webkit-scrollbar-thumb {
      background: #ff6b9d;
      border-radius: 4px;
    }

    @media (max-width: 768px) {
      .container {
        flex-direction: column;
      }

      .sidebar {
        width: 100%;
        border-right: none;
        border-bottom: 4px solid #ffc1e3;
        max-height: 200px;
      }

      .main {
        flex: 1;
      }

      .header-right {
        flex-direction: column;
      }

      .message {
        max-width: 90%;
      }

      .bubble {
        max-width: 100%;
      }
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- SIDEBAR -->
    <div class="sidebar">
      <div class="sidebar-header">
        <div class="brand">
          <div class="brand-logo">📚</div>
          <div class="brand-text">
            <h1>Study Buddy</h1>
            <p>Chat with your docs! 📚</p>
          </div>
        </div>
        <button class="new-chat-btn">+ New Chat</button>
      </div>

      <div class="sidebar-conversations" id="conversations">
        <!-- Conversations appear here -->
      </div>

      <div class="sidebar-footer">
        ❤️ Made with love ✨
      </div>
    </div>

    <!-- MAIN CHAT -->
    <div class="main">
      <div class="header">
        <div class="header-left">
          <h2 id="chatTitle">Welcome to Study Buddy</h2>
          <div class="doc-pills" id="docPills"></div>
        </div>
        <div class="header-right">
          <div class="provider-selector">
            <label>Provider:</label>
            <select id="providerSelect">
              <option value="google">Google</option>
              <option value="ollama">Ollama</option>
            </select>
            <button id="applyProvider">Apply</button>
          </div>
          <div class="flashcard-control">
            <label for="flashcardCount">Cards:</label>
            <select id="flashcardCountSelect">
              <option value="4">4</option>
              <option value="5">5</option>
              <option value="10">10</option>
              <option value="15">15</option>
            </select>
            <button class="mode-btn flashcard-btn" id="flashcardBtn">📚 Flashcards</button>
          </div>
          <div class="quiz-control">
            <label for="quizCount">Questions:</label>
            <select id="quizCountSelect">
              <option value="3">3</option>
              <option value="5">5</option>
              <option value="10">10</option>
            </select>
            <button class="mode-btn quiz-btn" id="quizBtn">🧠 Quiz</button>
          </div>
        </div>
      </div>

      <div class="messages" id="messages">
        <div class="message bot">
          <div class="mascot happy">^_^</div>
          <div>
            <div class="bubble">Hi there! 🌸 I'm your Study Buddy! Upload a document and ask me anything, or I can create flashcards and quizzes for you!</div>
            <div class="message-time">10:30 AM</div>
          </div>
        </div>
      </div>

      <div class="input-area">
        <button class="upload-btn" id="uploadBtn" title="Upload PDF">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M12 19V5" />
            <path d="M5 12l7-7 7 7" />
            <path d="M5 19h14" />
          </svg>
        </button>
        <input type="file" id="pdfInput" accept=".pdf" style="display: none;" />
        <div class="input-wrapper">
          <textarea id="messageInput" placeholder="Ask me anything about your documents... ✨" rows="1"></textarea>
          <span style="color: #ffc1e3;">✨</span>
        </div>
        <button class="mode-toggle" id="modeToggle" title="Switch response mode">Mode: Normal</button>
        <button class="send-btn" id="sendBtn" title="Send">→</button>
      </div>
    </div>
  </div>

  <!-- FLASHCARD MODAL -->
  <div class="modal" id="flashcardModal">
    <div class="modal-content">
      <button class="modal-close" id="closeFlashcard">✕</button>
      <div class="modal-header">
        <div class="modal-icon flashcard">📚</div>
        <div>
          <h2>Your Flashcards!</h2>
          <p id="flashcardCount">Loading...</p>
        </div>
      </div>
      <div class="flashcards-grid" id="flashcardsContainer"></div>
    </div>
  </div>

  <!-- QUIZ MODAL -->
  <div class="modal" id="quizModal">
    <div class="modal-content">
      <button class="modal-close" id="closeQuiz">✕</button>
      <div class="modal-header">
        <div class="modal-icon quiz">🧠</div>
        <div>
          <h2>Quiz Time!</h2>
          <p id="quizCount">Loading...</p>
        </div>
      </div>
      <div class="quiz-questions" id="quizContainer"></div>
      <div class="modal-footer">⭐ Keep going! You're doing great! ✨</div>
    </div>
  </div>

  <script>
    const MODE_OPTIONS = [
      { id: 'normal', label: 'Normal' },
      { id: 'explain_simple', label: 'Explain Simply' },
      { id: 'summarize', label: 'Summarize' },
    ];

    const state = {
      currentChat: null,
      chats: {},
      mascotState: 'happy',
      flashcards: [],
      quizzes: [],
      currentModeIndex: 0,
    };

    // DOM Elements - declare globally
    let uploadBtn, pdfInput, messageInput, sendBtn, modeToggle, messagesContainer;
    let flashcardBtn, quizBtn, flashcardModal, quizModal;
    let closeFlashcard, closeQuiz, docPills, chatTitle;
    let conversationsContainer, providerSelect, applyProvider;

    document.addEventListener('DOMContentLoaded', function() {
      // Initialize DOM elements after page loads
      initializeDOMElements();
      
      // Create first chat
      createNewChat();
      
      // Render initial state
      renderConversations();
      loadProvider();
      
      // Attach event listeners
      uploadBtn.addEventListener('click', () => pdfInput.click());
      pdfInput.addEventListener('change', handleFileUpload);
      messageInput.addEventListener('input', autoResizeTextarea);
      messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });
      sendBtn.addEventListener('click', sendMessage);
      modeToggle.addEventListener('click', cycleMode);
      flashcardBtn.addEventListener('click', () => generateFlashcards());
      quizBtn.addEventListener('click', () => generateQuiz());
      closeFlashcard.addEventListener('click', () => flashcardModal.classList.remove('active'));
      closeQuiz.addEventListener('click', () => quizModal.classList.remove('active'));
      applyProvider.addEventListener('click', switchProvider);
      document.querySelector('.new-chat-btn').addEventListener('click', () => {
        createNewChat();
        messageInput.focus();
      });

      // initial mode label
      updateModeButton();
    });

    // Create initial chat session
    function createNewChat() {
      const chatId = Date.now().toString();
      const now = new Date();
      const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      
      state.chats[chatId] = {
        id: chatId,
        title: `Chat ${Object.keys(state.chats).length + 1}`,
        messages: [
          { sender: 'bot', text: 'Hi there! 🌸 I\'m your Study Buddy! Upload a document and ask me anything, or I can create flashcards and quizzes for you!', time: timeStr, type: 'normal' }
        ],
        uploadedDocs: [],
        docId: null,
        createdAt: now,
      };
      
      state.currentChat = chatId;
      renderConversations();
      renderMessages();
      return chatId;
    }

    // Initialize DOM elements after page loads
    function initializeDOMElements() {
      uploadBtn = document.getElementById('uploadBtn');
      pdfInput = document.getElementById('pdfInput');
      messageInput = document.getElementById('messageInput');
      sendBtn = document.getElementById('sendBtn');
      modeToggle = document.getElementById('modeToggle');
      messagesContainer = document.getElementById('messages');
      flashcardBtn = document.getElementById('flashcardBtn');
      quizBtn = document.getElementById('quizBtn');
      flashcardModal = document.getElementById('flashcardModal');
      quizModal = document.getElementById('quizModal');
      closeFlashcard = document.getElementById('closeFlashcard');
      closeQuiz = document.getElementById('closeQuiz');
      docPills = document.getElementById('docPills');
      chatTitle = document.getElementById('chatTitle');
      conversationsContainer = document.getElementById('conversations');
      providerSelect = document.getElementById('providerSelect');
      applyProvider = document.getElementById('applyProvider');
    }

    async function handleFileUpload(e) {
      const file = e.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch('/rag/ingest/pdf', { method: 'POST', body: formData });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        
        const chat = state.chats[state.currentChat];
        chat.docId = data.doc_id;
        chat.uploadedDocs.push({ id: data.doc_id, name: file.name });
        renderDocPills();
        addBotMessage(`Document "${file.name}" uploaded successfully! 📄`);
      } catch (err) {
        addBotMessage(`Upload failed: ${err.message}`, 'error');
      }
      
      // Reset file input
      pdfInput.value = '';
    }

    function autoResizeTextarea() {
      messageInput.style.height = 'auto';
      messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    }

    function updateModeButton() {
      const mode = MODE_OPTIONS[state.currentModeIndex];
      if (modeToggle) {
        modeToggle.textContent = `Mode: ${mode.label}`;
      }
    }

    function cycleMode() {
      state.currentModeIndex = (state.currentModeIndex + 1) % MODE_OPTIONS.length;
      updateModeButton();
    }

    async function sendMessage() {
      const text = messageInput.value.trim();
      if (!text) return;

      const mode = MODE_OPTIONS[state.currentModeIndex];
      const chat = state.chats[state.currentChat];

      if (mode.id === 'summarize' && !chat.docId) {
        addBotMessage('Please upload a document first to summarize! 📄', 'error');
        return;
      }

      addUserMessage(text);
      messageInput.value = '';
      messageInput.style.height = 'auto';
      setMascot('thinking');

      try {
        let inputText = text;
        let modeToSend = 'explain';
        if (mode.id === 'summarize') {
          modeToSend = 'summarize';
        } else if (mode.id === 'explain_simple') {
          inputText = `${text} (Explain simply)`;
        }

        const res = await fetch('/agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            mode: modeToSend,
            input: inputText,
            doc_id: chat.docId || null,
          }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        if (data.message) {
          addBotMessage(data.message, 'normal', data.sources || []);
        }
      } catch (err) {
        addBotMessage(`Error: ${err.message}`, 'error', []);
      } finally {
        setMascot('happy');
      }
    }

    async function generateFlashcards() {
      const chat = state.chats[state.currentChat];
      if (!chat.docId) {
        addBotMessage('Please upload a document first to generate flashcards! 📄', 'error');
        return;
      }

      setMascot('thinking');
      try {
        const numFlashcards = parseInt(document.getElementById('flashcardCountSelect').value) || 4;
        const res = await fetch('/agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            mode: 'flashcards',
            input: 'Generate flashcards',
            doc_id: chat.docId,
            num_questions: numFlashcards,
          }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        state.flashcards = data.flashcards || [];
        renderFlashcards();
        flashcardModal.classList.add('active');
        setMascot('excited');
        setTimeout(() => setMascot('happy'), 2000);
      } catch (err) {
        addBotMessage(`Error generating flashcards: ${err.message}`, 'error');
        setMascot('happy');
      }
    }

    async function generateQuiz() {
      const chat = state.chats[state.currentChat];
      if (!chat.docId) {
        addBotMessage('Please upload a document first to generate quizzes! 📄', 'error');
        return;
      }

      setMascot('thinking');
      try {
        const numQuestions = parseInt(document.getElementById('quizCountSelect').value) || 3;
        const res = await fetch('/agent', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            mode: 'mcq',
            input: 'Generate quiz questions',
            doc_id: chat.docId,
            num_questions: numQuestions,
            include_explanations: true,
          }),
        });

        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);

        state.quizzes = data.mcq?.questions || [];
        renderQuiz();
        quizModal.classList.add('active');
        setMascot('excited');
        setTimeout(() => setMascot('happy'), 2000);
      } catch (err) {
        addBotMessage(`Error generating quiz: ${err.message}`, 'error');
        setMascot('happy');
      }
    }

    function renderFlashcards() {
      const container = document.getElementById('flashcardsContainer');
      document.getElementById('flashcardCount').textContent = `${state.flashcards.length} cards`;

      container.innerHTML = state.flashcards
        .map(
          (fc, idx) => `
        <div class="flashcard" data-idx="${idx}">
          <div class="flashcard-inner">
            <div class="flashcard-face flashcard-front">
              <div class="flashcard-label">Card ${idx + 1}</div>
              <p style="font-weight: 600; font-size: 16px;">${escapeHtml(fc.question)}</p>
            </div>
            <div class="flashcard-face flashcard-back">
              <div>
                <p style="font-weight: 600; margin: 0 0 12px 0;">Answer</p>
                <p>${escapeHtml(fc.answer)}</p>
                ${fc.mnemonic ? `<p style="font-size: 12px; color: #6b6674; margin-top: 8px;">Tip: ${escapeHtml(fc.mnemonic)}</p>` : ''}
              </div>
            </div>
          </div>
        </div>
      `
        )
        .join('');

      document.querySelectorAll('.flashcard').forEach((card) => {
        card.addEventListener('click', () => card.classList.toggle('flipped'));
      });
    }

    function renderQuiz() {
      const container = document.getElementById('quizContainer');
      document.getElementById('quizCount').textContent = `${state.quizzes.length} questions`;

      container.innerHTML = state.quizzes
        .map(
          (q, idx) => `
        <div class="quiz-question" data-q="${idx}">
          <div class="question-num">${idx + 1}</div>
          <div class="question-text">${escapeHtml(q.question)}</div>
          <div class="options">
            ${q.options
              .map(
                (opt, oIdx) => `
              <button class="option-btn" data-correct="${opt.is_correct}" onclick="handleQuizAnswer(this, ${q.id || idx})">
                <span style="font-weight: 700; font-family: Rubik; margin-right: 8px;">${escapeHtml(opt.label)}</span>
                ${escapeHtml(opt.text)}
              </button>
            `
              )
              .join('')}
          </div>
        </div>
      `
        )
        .join('');
    }

    window.handleQuizAnswer = function (btn, qIdx) {
      if (btn.parentElement.querySelector('.selected, .correct, .wrong')) return;

      const isCorrect = btn.dataset.correct === 'true' || btn.dataset.correct === 'True';
      btn.classList.add(isCorrect ? 'correct' : 'wrong');

      if (isCorrect) {
        setMascot('excited');
        setTimeout(() => setMascot('happy'), 1500);
      }
    };

    function renderDocPills() {
      const chat = state.chats[state.currentChat];
      docPills.innerHTML = chat.uploadedDocs
        .map(
          (doc) => `
        <div class="doc-pill" style="background-color: #ffc1e3; color: #7c2c4f;">
          <span>📄 ${doc.name}</span>
          <span class="doc-pill-close" onclick="removeDoc('${doc.id}')">✕</span>
        </div>
      `
        )
        .join('');
    }

    function removeDoc(docId) {
      const chat = state.chats[state.currentChat];
      chat.uploadedDocs = chat.uploadedDocs.filter(d => d.id !== docId);
      if (chat.uploadedDocs.length === 0) {
        chat.docId = null;
      }
      renderDocPills();
    }

    // Expose globally for onclick handlers
    window.removeDoc = removeDoc;

    function renderConversations() {
      conversationsContainer.innerHTML = Object.values(state.chats)
        .sort((a, b) => b.createdAt - a.createdAt)
        .map(
          (chat) => {
            const lastMsg = chat.messages.length > 0 
              ? chat.messages[chat.messages.length - 1].text.substring(0, 40) + '...'
              : 'No messages yet';
            const timeStr = chat.createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
            return `
        <div class="conv-item ${chat.id === state.currentChat ? 'active' : ''}" onclick="switchConversation('${chat.id}')">
          <div class="conv-title">${chat.title}</div>
          <div class="conv-preview">${escapeHtml(lastMsg)}</div>
          <div class="conv-time">${timeStr}</div>
        </div>
      `;
          }
        )
        .join('');
    }

    function switchConversation(chatId) {
      state.currentChat = chatId;
      const chat = state.chats[chatId];
      chatTitle.textContent = chat.title;
      renderConversations();
      renderMessages();
      renderDocPills();
    }

    // Expose globally for onclick handlers
    window.switchConversation = switchConversation;

    function addUserMessage(text) {
      const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const chat = state.chats[state.currentChat];
      chat.messages.push({ sender: 'user', text, time });
      renderMessages();
      renderConversations();
    }

    function addBotMessage(text, type = 'normal', citations = []) {
      const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      const chat = state.chats[state.currentChat];
      chat.messages.push({ sender: 'bot', text, time, type, citations });
      renderMessages();
    }

    function renderMessages() {
      const chat = state.chats[state.currentChat];
      messagesContainer.innerHTML = chat.messages
        .map(
          (msg) => {
            const citationsHtml = msg.citations && msg.citations.length > 0 
              ? `
                <div class="citations-container collapsed" onclick="toggleCitations(event)">
                  <div class="citations-title">
                    <span>📚 Sources (${msg.citations.length})</span>
                    <span class="citations-toggle">▼</span>
                  </div>
                  <div class="citations-content">
                    ${msg.citations.map((c, idx) => {
                      // Handle both object citations and string citations
                      if (typeof c === 'string') {
                        return `<div class="citation-item">${escapeHtml(c)}</div>`;
                      } else if (typeof c === 'object' && c !== null) {
                        const chunkId = c.chunk_id || `chunk_${idx}`;
                        const score = c.score ? (typeof c.score === 'number' ? c.score.toFixed(3) : c.score) : 'N/A';
                        const text = c.text ? escapeHtml(c.text) : 'No text available';
                        return `
                          <div class="citation-item">
                            <strong>${escapeHtml(chunkId)}</strong>
                            <div class="citation-score">Relevance: ${score}</div>
                            <div class="citation-text">${text}</div>
                          </div>
                        `;
                      }
                      return '';
                    }).join('')}
                  </div>
                </div>
              `
              : '';
            
            return `
        <div class="message ${msg.sender}">
          ${
            msg.sender === 'bot'
              ? `
            <div class="mascot ${state.mascotState}">
              ${state.mascotState === 'thinking' ? '◯.◯' : state.mascotState === 'excited' ? '★_★' : '^_^'}
            </div>
          `
              : ''
          }
          <div>
            <div class="bubble" style="${msg.type === 'error' ? 'background: #fee2e2; border-color: #f87171; color: #7f1d1d;' : ''}">${escapeHtml(msg.text)}</div>
            ${citationsHtml}
            <div class="message-time">${msg.time}</div>
          </div>
        </div>
      `;
          }
        )
        .join('');
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function setMascot(newState) {
      state.mascotState = newState;
      renderMessages();
    }

    function toggleCitations(event) {
      const container = event.currentTarget;
      container.classList.toggle('collapsed');
      event.stopPropagation();
    }

    // Expose globally
    window.toggleCitations = toggleCitations;

    function escapeHtml(text) {
      const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
      return text.replace(/[&<>"']/g, (m) => map[m]);
    }

    async function loadProvider() {
      try {
        const res = await fetch('/providers');
        const data = await res.json();
        providerSelect.value = data.llm_provider;
      } catch {
        console.error('Failed to load provider');
      }
    }

    async function switchProvider() {
      const provider = providerSelect.value;
      try {
        const res = await fetch('/providers/switch', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            llm_provider: provider,
            embedding_provider: provider,
          }),
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail);
        addBotMessage(`✓ Switched to ${provider} provider!`);
      } catch (err) {
        addBotMessage(`Provider switch failed: ${err.message}`, 'error');
        loadProvider();
      }
    }
  </script>
</body>
</html>
"""


@ui_router.get("/app", response_class=HTMLResponse)
async def serve_app() -> HTMLResponse:
    """Serve the single-page UI at /app."""
    return HTMLResponse(content=APP_HTML)


@ui_router.get("/", response_class=HTMLResponse)
async def serve_root() -> HTMLResponse:
    """Serve the single-page UI at root."""
    return HTMLResponse(content=APP_HTML)
