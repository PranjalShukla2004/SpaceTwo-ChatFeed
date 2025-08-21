export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'
export async function sendChat(payload: any){
  const res = await fetch(`${API_BASE}/api/chat`,{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  })
  if(!res.ok) throw new Error('Chat request failed')
  return res.json()
}
