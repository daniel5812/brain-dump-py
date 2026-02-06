// debug_note_flow.mjs
// Run: node debug_note_flow.mjs

const BASE_URL = "https://brain-dump-py.onrender.com";
const TECHNICAL_ID = "Daniel_iPhone"; // שים פה את ה-TechnicalID האמיתי שלך
const NOTE_TEXT = "פתק עם רעיון לפרויקט חדש"; // טקסט שמפעיל note

function assert(cond, msg) {
    if (!cond) throw new Error("ASSERT FAILED: " + msg);
}

async function getJson(url, options = {}) {
    const res = await fetch(url, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
    });

    const text = await res.text();
    let json;
    try {
        json = JSON.parse(text);
    } catch {
        throw new Error(
            `Non-JSON response from ${url}\nStatus: ${res.status}\nBody:\n${text}`
        );
    }
    return { status: res.status, ok: res.ok, json };
}

(async () => {
    console.log("=== 1) VERIFY USER ===");
    const verifyUrl = `${BASE_URL}/verify-user?user_id=${encodeURIComponent(TECHNICAL_ID)}`;
    const verify = await getJson(verifyUrl, { method: "GET" });

    console.log("HTTP:", verify.status, "OK:", verify.ok);
    console.log("JSON:", verify.json);

    // אופציונלי: אם אתה עובד עם registration_url
    if (verify.json?.registration_url) {
        console.log("\nUser needs registration. registration_url:");
        console.log(verify.json.registration_url);
        console.log("Stop here (this matches the shortcut behavior).");
        return;
    }

    console.log("\n=== 2) BRAIN DUMP POST ===");
    const postUrl = `${BASE_URL}/brain-dump`;
    const body = {
        user_id: TECHNICAL_ID, // אם אצלך POST כבר דורש phone, החלף כאן ל-phone
        text: NOTE_TEXT,
    };

    const bd = await getJson(postUrl, {
        method: "POST",
        body: JSON.stringify(body),
    });

    console.log("HTTP:", bd.status, "OK:", bd.ok);
    console.log("JSON:", bd.json);

    console.log("\n=== 3) VALIDATE NOTE CONTRACT ===");
    // חוזה קשיח ל-Note:
    // { status: "SUCCESS", intent: "note", message: "<string>" }
    assert(typeof bd.json === "object" && bd.json !== null, "Response must be an object");
    assert("status" in bd.json, "Missing 'status'");
    assert("intent" in bd.json, "Missing 'intent'");
    assert("message" in bd.json, "Missing 'message'");

    console.log("status:", bd.json.status);
    console.log("intent:", bd.json.intent);
    console.log("message (type):", typeof bd.json.message);
    console.log("message (value):\n" + bd.json.message);

    if (bd.json.intent === "note") {
        assert(bd.json.status === "SUCCESS", "For note, status must be SUCCESS");
        assert(typeof bd.json.message === "string", "For note, message must be a string");
        assert(bd.json.message.trim().length > 0, "For note, message must not be empty");
        console.log("\n✅ NOTE CONTRACT OK. This is exactly what the Shortcut should append.");
    } else {
        console.log("\nℹ️ intent is not 'note' for this input. Try different NOTE_TEXT.");
    }
})().catch((e) => {
    console.error("\n❌ ERROR:", e.message);
    process.exit(1);
});
