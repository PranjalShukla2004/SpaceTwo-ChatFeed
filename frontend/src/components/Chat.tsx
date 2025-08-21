import { useRef, useState } from 'react'
import { sendChat } from '../lib/api'
import RecommendationCard from './RecommendationCard'

type Msg = { role:'user'|'assistant'; content:string; recs?: any[] }

export default function Chat(){
  const [messages, setMessages] = useState<Msg[]>([
    { role:'assistant', content: 'Hey! Drop a brief or describe your style. I can line up the right people.' }
  ])
  const [input, setInput] = useState('')
  const threadId = useRef(crypto.randomUUID())

  async function onSend(){
    const text = input.trim()
    if(!text) return
    const next = [...messages, { role:'user' as const, content:text }]
    setMessages(next)
    setInput('')
    try{
      const res = await sendChat({
        thread_id: threadId.current,
        messages: next.map(m=>({role:m.role, content:m.content}))
      })
      const assistantMsg: Msg = { role:'assistant', content: res.reply, recs: res.recommendations }
      setMessages(prev=>[...prev, assistantMsg])
    }catch(e:any){
      setMessages(prev=>[...prev, { role:'assistant', content: 'Oops, something went wrong.' }])
    }
  }

  return (
    <div className="space-y-3">
      <div className="space-y-3">
        {messages.map((m, i)=> (
          <div key={i} className={m.role==='user' ? 'text-right' : 'text-left'}>
            <div className={
              'inline-block max-w-[80%] px-4 py-2 rounded-2xl ' +
              (m.role==='user' ? 'bg-white text-black' : 'bg-white/10')
            }>{m.content}</div>
            {m.recs && m.recs.length>0 && (
              <div className="mt-3 space-y-2">
                {m.recs.map((r:any)=> <RecommendationCard key={r.id} rec={r} />)}
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="flex gap-2">
        <input
          value={input}
          onChange={e=>setInput(e.target.value)}
          onKeyDown={e=> e.key==='Enter' && onSend()}
          placeholder="e.g., Need a lo‑fi video editor for a 30s TikTok"
          className="flex-1 px-4 py-3 rounded-2xl bg-white/10 outline-none"
        />
        <button onClick={onSend} className="px-5 py-3 rounded-2xl bg-white text-black font-medium">Send</button>
      </div>
    </div>
  )
}
