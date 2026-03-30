// import logo from './logo.svg';
import './App.css';
import { useState } from "react";

function App() {
  const [url, setUrl] = useState("");
  const [videoLang, setVideoLang] = useState("en");
  const [translateLang, setTranslateLang] = useState("es");
  const [result, setResult] = useState(null); // store API response
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventdefault();
    setLoading(true); // show loading state
    setResult(null); // clear previous result
    console.log({
      url,
      videoLang,
      translateLang,
    });

    // send to backend FastAPI:
    try {
      const response = await fetch("http://127.0.0.1:8000/subtitles", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          video_url: url,
          video_language: videoLang,
          target_language: translateLang,
        }),
      });

      const data = await response.json();
      setResult(data); // save API response results
      console.log(data)
    } catch (error) {
      setResult({ error: "Failed to fetch from backend" });
    }

    setLoading(false);
  }

  return (
    <div style={{ padding: "20px" }}>
      <h1>loqio: Multi-Language Video Transcription</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>YouTube Video URL: </label> <br/>
          <input 
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://www.youtube.com/"
            style={{ width: "400px" }}
          />
        </div>

        <br/>

        <div>
          <label>Original Video Language: </label> <br/>
          <select 
            value={videoLang}
            onChange={(e) => setVideoLang(e.target.value)}
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="zh">Mandarin</option>
            <option value="kr">Korean</option>
          </select>
        </div>

        <br/>

        <div>
          <label>Language to Translate Video Subtitles to:</label> <br/>
          <select
            value={translateLang}
            onChange={(e) => setTranslateLang(e.target.value)}
          >
            <option value="en">English</option>
          </select>
        </div>

        <br/>

        <button type="submit">Submit</button>
      </form>
      
      <br/>

      {loading && <p>Processing...</p>}

      {result && (
        <div>
          <h3>Response from backend:</h3>
          <pre>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default App;
