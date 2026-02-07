// debug_reminder_flow.mjs
// Run: node debug_reminder_flow.mjs

const BASE_URL = "https://brain-dump-py.onrender.com";
const TECHNICAL_ID = "Daniel_iPhone";

// Test cases
const TEST_WITH_TIME = "תזכיר לי מחר בשעה 5 אחה״צ להתקשר לאמא";
const TEST_WITHOUT_TIME = "תזכיר לי להתקשר לאמא";

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

async function testReminder(text, description) {
    console.log(`\n${"=".repeat(60)}`);
    console.log(`TEST: ${description}`);
    console.log(`TEXT: "${text}"`);
    console.log("=".repeat(60));

    const postUrl = `${BASE_URL}/brain-dump`;
    const body = {
        user_id: TECHNICAL_ID,
        text: text,
    };

    const bd = await getJson(postUrl, {
        method: "POST",
        body: JSON.stringify(body),
    });

    console.log("HTTP:", bd.status, "OK:", bd.ok);
    console.log("\nJSON Response:");
    console.log(JSON.stringify(bd.json, null, 2));

    // Validate reminder contract
    console.log("\n--- CONTRACT VALIDATION ---");

    if (bd.json.intent !== "reminder") {
        console.log("⚠️  Intent is not 'reminder':", bd.json.intent);
        console.log("(Server may need deployment for new code)");
        return;
    }

    console.log("✅ intent:", bd.json.intent);
    console.log("✅ status:", bd.json.status);
    console.log("✅ message:", bd.json.message);
    console.log("✅ reminder_title:", bd.json.reminder_title);
    console.log("✅ reminder_time:", bd.json.reminder_time, "(HH:MM format)");
    console.log("✅ reminder_date:", bd.json.reminder_date, "(YYYY-MM-DD format)");

    if (bd.json.status === "NEEDS_CLARIFICATION") {
        console.log("✅ clarification_for:", bd.json.clarification_for);
        console.log("\n📱 Shortcut should ASK USER for time");
    } else if (bd.json.status === "SUCCESS") {
        console.log("\n📱 Shortcut should CREATE REMINDER with:");
        console.log("   Title:", bd.json.reminder_title);
        console.log("   Time:", bd.json.reminder_time);
        console.log("   Date:", bd.json.reminder_date);
    }
}

(async () => {
    console.log("🔔 REMINDER FLOW DEBUG SCRIPT\n");
    console.log("Expected JSON format:");
    console.log({
        status: "SUCCESS | NEEDS_CLARIFICATION",
        intent: "reminder",
        message: "הודעה למשתמש",
        reminder_title: "כותרת התזכורת",
        reminder_time: "HH:MM (e.g., 17:00)",
        reminder_date: "YYYY-MM-DD (e.g., 2026-02-06)",
        clarification_for: "time (when missing)"
    });

    // Test 1: Without time (should need clarification)
    await testReminder(TEST_WITHOUT_TIME, "Without time → NEEDS_CLARIFICATION");

    // Test 2: With time (should succeed)
    await testReminder(TEST_WITH_TIME, "With time → SUCCESS");

})().catch((e) => {
    console.error("\n❌ ERROR:", e.message);
    process.exit(1);
});
