import sys

with open('frontend/src/app/scan/page.tsx', 'r') as f:
    code = f.read()

replacement = '''          <div className="flex gap-4 mb-6">
            {['url', 'sms', 'email', 'qr'].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setType(t)}
                className={\lex-1 py-3 px-4 rounded-xl font-medium border transition-all \\}
              >
                {t === 'url' && <Link className="w-5 h-5 mx-auto mb-2" />}
                {t === 'sms' && <MessageSquare className="w-5 h-5 mx-auto mb-2" />}
                {t === 'email' && <FileText className="w-5 h-5 mx-auto mb-2" />}
                {t === 'qr' && <Search className="w-5 h-5 mx-auto mb-2" />}
                {t.toUpperCase()}
              </button>
            ))}
          </div>'''

code = code.replace('''          <div className="flex gap-4 mb-4">
             <select 
               value={type} 
               onChange={(e) => setType(e.target.value)}
               className="bg-black/50 border border-slate-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
             >
               <option value="url">URL</option>
               <option value="sms">SMS</option>
               <option value="email">Email</option><option value="qr">QR Code</option>
             </select>
          </div>''', replacement)

with open('frontend/src/app/scan/page.tsx', 'w') as f:
    f.write(code)
