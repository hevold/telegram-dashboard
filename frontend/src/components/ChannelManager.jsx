import { useState, useEffect } from "react";
import { getChannels, addChannel, toggleChannel, deleteChannel } from "../api";

export default function ChannelManager({ onClose }) {
  const [channels, setChannels] = useState([]);
  const [username, setUsername] = useState("");
  const [name, setName] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    const data = await getChannels();
    setChannels(data);
  };

  useEffect(() => { load(); }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!username.trim()) return;
    setSaving(true);
    setError("");
    try {
      await addChannel({ username: username.replace("@", "").trim(), name: name.trim() || null });
      setUsername("");
      setName("");
      await load();
    } catch (err) {
      setError(err.response?.data?.detail ?? "Kunne ikke legge til kanal");
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (id) => {
    await toggleChannel(id);
    await load();
  };

  const handleDelete = async (id) => {
    if (confirm("Fjerne kanalen?")) {
      await deleteChannel(id);
      await load();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg w-full max-w-md border border-gray-700">
        <div className="flex items-center justify-between px-4 py-3 border-b border-gray-700">
          <h2 className="font-semibold">Telegram-kanaler</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white">✕</button>
        </div>

        <div className="p-4">
          <form onSubmit={handleAdd} className="flex gap-2 mb-4">
            <input
              className="flex-1 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              placeholder="@kanalbrukernavn"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />
            <input
              className="w-32 bg-gray-800 border border-gray-700 rounded px-3 py-2 text-sm"
              placeholder="Visningsnavn"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <button
              type="submit"
              disabled={saving}
              className="px-3 py-2 rounded bg-blue-600 text-sm font-medium hover:bg-blue-500 disabled:opacity-50"
            >
              Legg til
            </button>
          </form>

          {error && <p className="text-red-400 text-sm mb-3">{error}</p>}

          <div className="space-y-2 max-h-80 overflow-y-auto">
            {channels.length === 0 && (
              <p className="text-gray-600 text-sm text-center py-4">
                Ingen kanaler lagt til ennå.
              </p>
            )}
            {channels.map((ch) => (
              <div
                key={ch.id}
                className="flex items-center justify-between bg-gray-800 rounded px-3 py-2"
              >
                <div>
                  <span className="text-sm font-medium">
                    {ch.name || `@${ch.username}`}
                  </span>
                  {ch.name && (
                    <span className="text-xs text-gray-500 ml-2">@{ch.username}</span>
                  )}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleToggle(ch.id)}
                    className={`px-2 py-0.5 rounded text-xs font-medium transition-colors ${
                      ch.active
                        ? "bg-emerald-700 hover:bg-emerald-600 text-white"
                        : "bg-gray-700 hover:bg-gray-600 text-gray-400"
                    }`}
                  >
                    {ch.active ? "Aktiv" : "Inaktiv"}
                  </button>
                  <button
                    onClick={() => handleDelete(ch.id)}
                    className="text-gray-600 hover:text-red-500 text-xs transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
