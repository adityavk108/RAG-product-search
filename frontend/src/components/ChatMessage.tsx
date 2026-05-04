import { ChatMessage as ChatMessageType } from '../types';

interface ChatMessageProps {
  message: ChatMessageType;
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-4 py-3 rounded-2xl ${
            isUser
              ? 'bg-indigo-500 text-white rounded-br-md'
              : 'bg-slate-800 text-slate-100 rounded-bl-md'
          }`}
        >
          <p className="whitespace-pre-wrap">{message.content}</p>
        </div>
        
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-3 pl-2">
            <p className="text-xs text-slate-500 mb-2">Relevant products:</p>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {message.sources.slice(0, 3).map((product) => (
                <div key={product.product_id} className="bg-slate-800 rounded-lg p-2">
                  <p className="text-xs font-medium text-slate-200 truncate">{product.name}</p>
                  <p className="text-xs text-indigo-400">
                    ₹{product.price.toLocaleString('en-IN')}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}