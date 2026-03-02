import { useState } from "react";
import { createEvent } from "../api";

export default function AddEventModal({ onClose, onSaved }) {
  const [form, setForm] = useState({
    source: "telegram",
    title: "",
    content: "",
    url: "",
    channel_name: "",
    latitude: "",
    longitude: "",
    location_name: "",
    manual_location: false,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError("");
    try {
      const payload = {
        ...form,
        latitude: form.latitude ? parseFloat(form.latitude) : null,
        longitude: form.longitude ? parseFloat(form.longitude) : null,
        manual_location: !!(form.latitude && form.longitude),
      };
      await createEvent(payload);
      onSaved();
    } catch (err) {
      setError(err.response?.data?.detail ?? "Noe gikk galt");
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg w-full max-w-md border border-gray-700">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
          <h2 className="font-semibold">Legg til hendelse manuelt</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white">✕</button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-3">
          {/* Source */}
          <div className="flex gap-2">
            {["telegram", "gdelt", "manual"].map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => set("source", s)}
                className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                  form.source === s
                    ? "bg-blue-600 text-white"
                    : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                }`}
              >
                {s}
              </button>
            ))}
          </div>

          <input
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
            placeholder="Tittel"
            value={form.title}
            onChange={(e) => set("title", e.target.value)}
          />

          <textarea
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm h-24 resize-none"
            placeholder="Innhold (brukes til automatisk geokoding hvis koordinater mangler)"
            value={form.content}
            onChange={(e) => set("content", e.target.value)}
          />

          <input
            className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
            placeholder="URL / lenke til post"
            value={form.url}
            onChange={(e) => set("url", e.target.value)}
          />

          {form.source === "telegram" && (
            <input
              className="w-full bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              placeholder="Kanalnavn (uten @)"
              value={form.channel_name}
              onChange={(e) => set("channel_name", e.target.value)}
            />
          )}

          <div className="border-t border-gray-700 pt-3">
            <p className="text-xs text-gray-500 mb-2">
              Koordinater (valgfritt – hentes automatisk fra innhold hvis tom)
            </p>
            <div className="flex gap-2">
              <input
                className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
                placeholder="Breddegrad (lat)"
                value={form.latitude}
                onChange={(e) => set("latitude", e.target.value)}
                type="number"
                step="any"
              />
              <input
                className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
                placeholder="Lengdegrad (lon)"
                value={form.longitude}
                onChange={(e) => set("longitude", e.target.value)}
                type="number"
                step="any"
              />
            </div>
            <input
              className="w-full mt-2 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              placeholder="Stedsnavn"
              value={form.location_name}
              onChange={(e) => set("location_name", e.target.value)}
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <div className="flex gap-2 pt-1">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded bg-gray-800 text-sm hover:bg-gray-700 transition-colors"
            >
              Avbryt
            </button>
            <button
              type="submit"
              disabled={saving}
              className="flex-1 py-2 rounded bg-blue-600 text-sm font-medium hover:bg-blue-500 disabled:opacity-50 transition-colors"
            >
              {saving ? "Lagrer..." : "Lagre"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
