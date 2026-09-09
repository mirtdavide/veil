interface IconRailProps {
  onOpenProfile: () => void
  onOpenSearch: () => void
  onOpenPendingRequests: () => void
}

function IconRail({ onOpenProfile, onOpenSearch, onOpenPendingRequests }: IconRailProps): React.JSX.Element {
  return (
    <div className="w-16 bg-bg-rail h-screen flex flex-col items-center gap-3 py-4">
      <button onClick={onOpenProfile} className="w-10 h-10 rounded-full bg-bg-secondary hover:bg-accent flex items-center justify-center text-text">
        P
      </button>
      <button onClick={onOpenSearch} className="w-10 h-10 rounded-full bg-bg-secondary hover:bg-accent flex items-center justify-center text-text">
        S
      </button>
      <button onClick={onOpenPendingRequests} className="w-10 h-10 rounded-full bg-bg-secondary hover:bg-accent flex items-center justify-center text-text">
        R
      </button>
    </div>
  )
}

export default IconRail