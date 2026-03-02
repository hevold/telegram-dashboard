import { format } from "date-fns";
import { nb } from "date-fns/locale";
import { deleteEvent } from "../api";

const SOURCE_COLORS = {
  telegram: "bg-blue-600",
  gdelt: "bg-emerald-600",
};

export default function EventFeed({ events, selectedEvent, onSelectEvent, onRefresh }) {
  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (confirm("Slett denne hendelsen?")) {
      await deleteEvent(id);
      onRefresh();
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b border-gray-800 text-xs text-gray-400 font-medium">
        {events.length} hendelser
      </div>

      <div className="flex-1 overflow-y-auto">
        {events.length === 0 && (
          <div className="p-4 text-center text-gray-600 text-sm">
            Ingen hendelser ennå.
          </div>
        )}

        {events.map((ev) => (
          <div
            key={ev.id}
            onClick={() => onSelectEvent(ev)}
            className={`px-3 py-2.5 border-b border-gray-800 cursor-pointer transition-colors hover:bg-gray-800 ${
              selectedEvent?.id === ev.id ? "bg-gray-800 border-l-2 border-l-blue-500" : ""
            }`}
          >
            <div className="flex items-start justify-between gap-1">
              <div className="flex items-center gap-1.5 min-w-0">
                <span
                  className={`shrink-0 px-1 py-0.5 rounded text-[10px] font-bold text-white ${
                    SOURCE_COLORS[ev.source] ?? "bg-gray-600"
                  }`}
                >
                  {ev.source === "telegram" ? "TG" : "GD"}
                </span>
                {ev.channel_name && (
                  <span className="text-gray-500 text-xs truncate">
                    @{ev.channel_name}
                  </span>
                )}
              </div>

              <button
                onClick={(e) => handleDelete(e, ev.id)}
                className="shrink-0 text-gray-700 hover:text-red-500 text-xs transition-colors"
                title="Slett"
              >
                ✕
              </button>
            </div>

            <p className="text-sm mt-1 leading-snug line-clamp-2 text-gray-200">
              {ev.title || "Ingen tittel"}
            </p>

            <div className="flex items-center gap-2 mt-1">
              {ev.location_name && (
                <span className="text-xs text-gray-500 truncate">
                  📍 {ev.location_name}
                </span>
              )}
              {!ev.latitude && (
                <span className="text-xs text-yellow-700">Ingen koordinater</span>
              )}
            </div>

            <p className="text-xs text-gray-600 mt-0.5">
              {ev.event_date
                ? format(new Date(ev.event_date), "d. MMM HH:mm", { locale: nb })
                : ""}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
