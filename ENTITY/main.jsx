import React from "react";
import { createRoot } from "react-dom/client";
import AIThinkingCard from "./AIThinkingCard.jsx";

function App() {
  return <AIThinkingCard />;
}

const rootElement = document.getElementById("root");

if (rootElement) {
  createRoot(rootElement).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}