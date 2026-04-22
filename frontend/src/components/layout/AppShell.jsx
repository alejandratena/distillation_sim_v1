import LibraryPanel from './LibraryPanel'
import Canvas from './Canvas'
import PropertyPanel from './PropertyPanel'

export default function AppShell() {
  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden"
      style={{ backgroundColor: 'var(--bg-primary)' }}>

      {/* Top Bar */}
      <header className="flex items-center justify-between px-4 py-2 border-b"
        style={{ backgroundColor: 'var(--bg-secondary)', borderColor: 'var(--border)' }}>
        <span className="text-sm font-semibold tracking-widest uppercase"
          style={{ color: 'var(--accent)' }}>
          Equilibria
        </span>
        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
          Mode: Academic
        </span>
        <span className="text-xs" style={{ color: 'var(--text-muted)' }}>
          ⚙
        </span>
      </header>

      {/* Three Panel Layout */}
      <div className="flex flex-1 overflow-hidden">
        <LibraryPanel />
        <Canvas />
        <PropertyPanel />
      </div>

    </div>
  )
}