import Chat from './components/Chat'

export default function App(){
  return (
    <div className="min-h-screen mx-auto max-w-3xl p-4 space-y-4">
      <header className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">SpacetwoChat</h1>
        <div className="text-sm opacity-70">Personalized Recommendations</div>
      </header>
      <Chat />
    </div>
  )
}
