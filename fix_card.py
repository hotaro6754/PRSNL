import os

filepath = 'frontend/src/app/(dashboard)/health/page.tsx'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

import re
content = re.sub(r'import \{ Card, CardContent, CardHeader, CardTitle \} from "@/components/ui/card";', '', content)
content = content.replace('<Card className="bg-slate-900 border-slate-800">', '<div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">')
content = content.replace('<Card className="bg-slate-900 border-slate-800 col-span-1">', '<div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden col-span-1">')
content = content.replace('</Card>', '</div>')

content = content.replace('<CardHeader className="flex flex-row items-center justify-between pb-2">', '<div className="flex flex-row items-center justify-between p-6 pb-2">')
content = content.replace('<CardHeader>', '<div className="p-6">')
content = content.replace('</CardHeader>', '</div>')

content = content.replace('<CardTitle className="text-sm font-medium text-slate-400">', '<h3 className="text-sm font-medium text-slate-400">')
content = content.replace('<CardTitle className="text-white flex items-center">', '<h3 className="text-lg font-semibold text-white flex items-center">')
content = content.replace('</CardTitle>', '</h3>')

content = content.replace('<CardContent>', '<div className="p-6 pt-0">')
content = content.replace('<CardContent className="h-[300px]">', '<div className="p-6 pt-0 h-[300px]">')
content = content.replace('<CardContent className="h-[400px] p-0 overflow-hidden rounded-b-xl border-t border-slate-800 bg-black">', '<div className="h-[400px] p-0 overflow-hidden rounded-b-xl border-t border-slate-800 bg-black">')
content = content.replace('</CardContent>', '</div>')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
