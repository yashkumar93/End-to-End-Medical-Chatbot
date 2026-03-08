function normalizeBackendUrl(rawUrl) {
    if (!rawUrl) {
        return "";
    }
    return rawUrl.replace(/\/+$/, "");
}

function extractMessage(req) {
    if (!req.body) {
        return "";
    }

    if (typeof req.body === "string") {
        const params = new URLSearchParams(req.body);
        return (params.get("msg") || "").trim();
    }

    if (typeof req.body === "object") {
        return String(req.body.msg || "").trim();
    }

    return "";
}

export default async function handler(req, res) {
    if (req.method !== "POST") {
        res.setHeader("Allow", "POST");
        return res.status(405).send("Method Not Allowed");
    }

    const backendBaseUrl = normalizeBackendUrl(process.env.RENDER_BACKEND_URL);
    if (!backendBaseUrl) {
        return res.status(500).send("Missing RENDER_BACKEND_URL environment variable");
    }

    const msg = extractMessage(req);
    if (!msg) {
        return res.status(400).send("Please enter a question.");
    }

    try {
        const upstreamResponse = await fetch(`${backendBaseUrl}/get`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            },
            body: new URLSearchParams({ msg }).toString(),
        });

        const text = await upstreamResponse.text();
        return res.status(upstreamResponse.status).send(text);
    } catch (error) {
        return res.status(502).send("Unable to reach backend service.");
    }
}
