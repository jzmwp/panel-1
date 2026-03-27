import { Routes, Route, NavLink } from "react-router-dom";
import { MessageSquare, Upload, FileText, BarChart3, HardHat } from "lucide-react";
import ChatPage from "./pages/ChatPage";
import UploadPage from "./pages/UploadPage";
import ReportsPage from "./pages/ReportsPage";
import DashboardPage from "./pages/DashboardPage";
import { cn } from "./lib/utils";

const NAV_ITEMS = [
  { to: "/", icon: MessageSquare, label: "Chat" },
  { to: "/upload", icon: Upload, label: "Upload" },
  { to: "/documents", icon: FileText, label: "Documents" },
  { to: "/dashboard", icon: BarChart3, label: "Dashboard" },
];

function Sidebar() {
  return (
    <aside className="w-16 md:w-56 bg-surface-raised border-r border-border flex flex-col shrink-0">
      <div className="h-14 flex items-center gap-2 px-4 border-b border-border">
        <HardHat className="w-6 h-6 text-mine-500 shrink-0" />
        <span className="hidden md:block font-semibold text-sm tracking-tight">
          Panel 1
        </span>
      </div>
      <nav className="flex-1 py-2">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-4 py-2.5 mx-2 rounded-lg text-sm transition-colors",
                isActive
                  ? "bg-mine-600/15 text-mine-400"
                  : "text-text-secondary hover:bg-surface-overlay hover:text-text-primary"
              )
            }
          >
            <Icon className="w-5 h-5 shrink-0" />
            <span className="hidden md:block">{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="p-3 border-t border-border hidden md:block">
        <div className="text-xs text-text-muted">LW101 — Panel 1</div>
        <div className="text-xs text-text-muted">Deputy / Shift / Strata</div>
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <div className="h-screen flex overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-hidden">
        <Routes>
          <Route path="/" element={<ChatPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/documents" element={<ReportsPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>
    </div>
  );
}
