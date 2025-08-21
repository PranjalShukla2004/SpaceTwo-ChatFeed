type Rec = {
  id: string;
  kind: 'collaborator' | 'project' | 'cluster';
  title: string;
  subtitle?: string;
  media_url?: string;
  score?: number;
  meta?: Record<string, any>;
}

export default function RecommendationCard({rec}:{rec:Rec}){
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-3 flex gap-3">
      {rec.media_url && (
        <img src={rec.media_url} alt="" className="w-20 h-20 object-cover rounded-xl"/>
      )}
      <div className="flex-1">
        <div className="font-semibold">{rec.title}</div>
        <div className="text-sm opacity-80">{rec.subtitle}</div>
        {rec.meta?.styles && (
          <div className="mt-1 text-xs opacity-70">{rec.meta.styles.join(' • ')}</div>
        )}
        <div className="mt-2 flex gap-2">
          <button className="px-3 py-1 rounded-full bg-white text-black text-sm">View</button>
          <button className="px-3 py-1 rounded-full border border-white/20 text-sm">Invite</button>
        </div>
      </div>
      {typeof rec.score === 'number' && (
        <div className="text-xs opacity-60">{rec.score.toFixed(2)}</div>
      )}
    </div>
  )
}
