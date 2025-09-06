// /api/ai.js  (Vercel Serverless Function)
import { GoogleGenerativeAI } from "@google/generative-ai";

export default async function handler(req, res) {
  // CORS (fine for same-origin; also helps local dev)
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Headers", "content-type");
  if (req.method === "OPTIONS") return res.status(200).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const { message, systemPrompt, history = [] } = req.body || {};

    const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" }); // or "gemini-1.5-pro"

    // Optional persona + chat memory
    const chat = model.startChat({
      history: [
        ...(systemPrompt
          ? [
              { role: "user", parts: [{ text: `SYSTEM: ${systemPrompt}` }] },
              { role: "model", parts: [{ text: "OK" }] },
            ]
          : []),
        ...history, // [{role:"user"|"model", parts:[{text:"..."}]}]
      ],
    });

    const result = await chat.sendMessage(message);
    const text = result.response.text();

    return res.status(200).json({ text });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ error: e?.message || "AI error" });
  }
}
