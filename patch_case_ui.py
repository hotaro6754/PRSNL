"""
Patch frontend/src/app/(dashboard)/cases/[id]/page.tsx to show the explanation layer
"""

with open('frontend/src/app/(dashboard)/cases/[id]/page.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

EXPLANATION_UI = """
          {/* EXPLANATION LAYER */}
          {caseData.explanation && (
            <div className="rounded-xl border border-slate-800 bg-[#0c0f17] flex flex-col overflow-hidden mt-6">
              <div className="p-5 border-b border-slate-800 flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-400" />
                <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">Risk Explanation</h3>
              </div>
              <div className="p-5 space-y-4 text-sm">
                <div>
                  <span className="font-bold text-slate-400">WHAT:</span>
                  <p className="text-white mt-1">{caseData.explanation.what}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400">WHY:</span>
                  <p className="text-white mt-1">{caseData.explanation.why}</p>
                </div>
                <div>
                  <span className="font-bold text-slate-400">EVIDENCE:</span>
                  <ul className="mt-2 space-y-1">
                    {(caseData.explanation.evidence_summary || []).map((ev: any, i: number) => (
                      <li key={i} className="text-slate-300 flex items-start gap-2">
                         <span className="text-red-500 mt-0.5">•</span> {ev}
                      </li>
                    ))}
                  </ul>
                </div>
                {caseData.explanation.action && (
                  <div>
                    <span className="font-bold text-slate-400">ACTION:</span>
                    <p className="text-green-400 mt-1">{caseData.explanation.action}</p>
                  </div>
                )}
                {caseData.explanation.uncertainty && (
                  <div className="mt-4 p-3 bg-slate-800/50 rounded border border-slate-700 text-slate-300">
                    <span className="font-bold text-slate-400">UNCERTAINTY: </span>
                    {caseData.explanation.uncertainty}
                  </div>
                )}
              </div>
            </div>
          )}
"""

# Insert it right below the Threat Narrative
if "Threat Narrative</h3>" in content and "Risk Explanation" not in content:
    import re
    # We find the Threat Narrative block and insert the Explanation layer after it
    pattern = r'(<div className="rounded-xl border border-slate-800 bg-\[#0c0f17\] p-5">.*?</div>)'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        content = content[:match.end()] + EXPLANATION_UI + content[match.end():]

with open('frontend/src/app/(dashboard)/cases/[id]/page.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patched cases/[id]/page.tsx")
