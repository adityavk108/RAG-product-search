import { useState, useRef, useEffect } from 'react';
import QueryInput from '../components/QueryInput';
import ChatMessage from '../components/ChatMessage';
import LoadingSpinner from '../components/LoadingSpinner';
import { useQuery } from '../hooks/useQuery';
import { ChatMessage as ChatMessageType } from '../types';

export default function QAPage() {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const { ask, loading } = useQuery();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (question: string) => {
    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
    };
    setMessages(prev => [...prev, userMessage]);

    try {
      const response = await ask(question);
      const assistantMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessageType = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col">
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-100 mb-2">Product Q&A</h1>
            <p className="text-slate-400">Ask questions about products and get AI-powered answers</p>
          </div>

          {messages.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 bg-indigo-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <p className="text-slate-400">Start a conversation by asking a question below</p>
              <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-lg mx-auto">
                <button
                  onClick={() => handleSubmit('What is the best phone under 50000?')}
                  className="px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 text-left transition-colors"
                >
                  What is the best phone under ₹50,000?
                </button>
                <button
                  onClick={() => handleSubmit('Recommend running shoes for men')}
                  className="px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 text-left transition-colors"
                >
                  Recommend running shoes for men
                </button>
                <button
                  onClick={() => handleSubmit('Which headphones are best for gaming?')}
                  className="px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 text-left transition-colors"
                >
                  Which headphones are best for gaming?
                </button>
                <button
                  onClick={() => handleSubmit('What is the best laptop for programming?')}
                  className="px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-lg text-slate-300 text-left transition-colors"
                >
                  What is the best laptop for programming?
                </button>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-slate-800 px-4 py-3 rounded-2xl rounded-bl-md">
                    <LoadingSpinner />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </div>

      <div className="border-t border-slate-700 bg-slate-800/50 backdrop-blur-sm">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <QueryInput onSubmit={handleSubmit} disabled={loading} />
        </div>
      </div>
    </div>
  );
}