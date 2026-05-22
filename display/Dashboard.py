import os
import json
import webbrowser

class DashboardModule:
    def __init__(self, model_name="gemma4:31b-cloud"):
        # model_name kept for backward compatibility; dashboard renders deterministically now.
        self.model_name = model_name
        self.base_template_path = "interface/base.html"
        self.output_file = "interface/dashboard.html"
        self.system_name = os.getenv("SUSTAINAI_SYSTEM_NAME", "SustainAi")
        self._opened = False

    def _read_base_template(self):
        try:
            with open(self.base_template_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            print("❌ Error: base.html not found. Please ensure it exists in the interface folder.")
            return None

    def _escape(self, value):
        if value is None:
            return ""
        return str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _render_kpi_card(self, label, value):
        return (
            "<div class='glass-premium p-6 rounded-2xl border border-slate-800 shadow-xl'>"
            f"<p class='text-xs text-slate-500 uppercase tracking-wider mb-2'>{self._escape(label)}</p>"
            f"<p class='text-2xl font-medium text-white'>{self._escape(value) if value not in (None, '') else 'N/A'}</p>"
            "</div>"
        )

    def _render_dashboard_body(self, payload: dict) -> str:
        header = payload.get("header") or {}
        hero = payload.get("hero") or []
        atmosphere = payload.get("atmosphere") or []
        soil = payload.get("soil") or []
        weather = payload.get("weather") or []
        risks = payload.get("risks") or []
        insights = payload.get("insights") or []
        research = payload.get("research") or []
        visuals = payload.get("visuals") or []
        diagnostics = payload.get("diagnostics") or []

        system_name = header.get("system_name") or self.system_name
        subtitle = header.get("subtitle") or "Live Environmental Waste Intelligence"
        location = header.get("location") or "Unknown"
        updated_at = header.get("updated_at") or "--"
        cache_status = header.get("cache_status") or "MISS"

        def render_metric_cards(items):
            if not items:
                return "<div class='text-slate-500 text-sm italic'>No metrics available.</div>"
            cards = []
            for item in items:
                label = item.get("label") or "Metric"
                value = item.get("value") or "N/A"
                cards.append(
                    "<div class='glass-premium p-4 rounded-2xl border border-slate-800 shadow-xl'>"
                    f"<p class='text-xs text-slate-500 uppercase tracking-wider mb-2'>{self._escape(label)}</p>"
                    f"<p class='text-lg font-semibold text-white'>{self._escape(value)}</p>"
                    "</div>"
                )
            return "<div class='grid grid-cols-1 md:grid-cols-3 gap-4'>" + "".join(cards) + "</div>"

        def render_hero(items):
            if not items:
                return ""
            cards = []
            for item in items:
                label = item.get("label") or "KPI"
                value = item.get("value") or "N/A"
                cards.append(
                    "<div class='glass-premium p-5 rounded-2xl border border-slate-800 shadow-xl gradient-card'>"
                    f"<p class='text-xs text-slate-400 uppercase tracking-widest mb-2'>{self._escape(label)}</p>"
                    f"<p class='text-3xl font-semibold text-white number-glow'>{self._escape(value)}</p>"
                    "</div>"
                )
            return "<div class='grid grid-cols-1 md:grid-cols-4 gap-4'>" + "".join(cards) + "</div>"

        def render_risks(items):
            if not items:
                return "<div class='text-slate-500 text-sm italic'>No risk scoring available.</div>"
            cards = []
            for item in items:
                label = item.get("label") or "Risk"
                score = item.get("score")
                level = item.get("level") or "LOW"
                note = item.get("note") or ""
                level_class = {
                    "LOW": "text-emerald-300",
                    "MODERATE": "text-amber-300",
                    "HIGH": "text-orange-300",
                    "SEVERE": "text-red-400",
                }.get(level, "text-slate-300")

                cards.append(
                    "<div class='glass-premium p-4 rounded-2xl border border-slate-800 shadow-xl space-y-2'>"
                    f"<div class='flex items-center justify-between'><p class='text-sm font-semibold text-white'>{self._escape(label)}</p>"
                    f"<span class='text-xs font-semibold uppercase {level_class}'>{self._escape(level)}</span></div>"
                    f"<p class='text-xl font-semibold text-white'>{self._escape(score)}</p>"
                    f"<p class='text-xs text-slate-400'>{self._escape(note)}</p>"
                    "</div>"
                )
            return "<div class='grid grid-cols-1 md:grid-cols-2 gap-4'>" + "".join(cards) + "</div>"

        def render_visuals(items):
            if not items:
                return "<div class='text-slate-500 text-sm italic'>No visuals available.</div>"
            cards = []
            for item in items:
                title = item.get("title") or "Visual"
                image = item.get("image")
                description = item.get("description") or ""
                if not image:
                    continue
                cards.append(
                    "<div class='glass-premium p-4 rounded-2xl border border-slate-800 shadow-xl space-y-3'>"
                    f"<p class='text-xs text-slate-400 uppercase tracking-wider'>{self._escape(title)}</p>"
                    f"<img src='{self._escape(image)}' class='rounded-xl border border-slate-700 w-full h-auto shadow-lg' alt='{self._escape(title)}' />"
                    f"<p class='text-sm text-slate-300 leading-relaxed'>{self._escape(description)}</p>"
                    "</div>"
                )
            return "<div class='grid grid-cols-1 md:grid-cols-2 gap-4'>" + "".join(cards) + "</div>"

        def render_insights(items):
            if not items:
                return "<div class='text-slate-500 text-sm italic'>No AI insights yet.</div>"
            cards = []
            for insight in items:
                cards.append(
                    "<div class='glass-premium p-4 rounded-2xl border border-slate-800 shadow-xl'>"
                    f"<p class='text-sm text-slate-200 leading-relaxed'>{self._escape(insight)}</p>"
                    "</div>"
                )
            return "<div class='grid grid-cols-1 md:grid-cols-2 gap-4'>" + "".join(cards) + "</div>"

        def render_research(items):
            if not items:
                return "<div class='text-slate-500 text-sm italic'>No research intelligence loaded.</div>"
            cards = []
            for item in items:
                title = item.get("title") or "Research"
                summary = item.get("summary") or ""
                link = item.get("link")
                image = item.get("image")
                link_html = ""
                if link:
                    link_html = f"<a class='text-xs text-cyan-300 hover:text-cyan-200' href='{self._escape(link)}' target='_blank' rel='noreferrer'>Read More</a>"
                image_html = ""
                if image:
                    image_html = (
                        f"<img src='{self._escape(image)}' alt='{self._escape(title)}' "
                        "class='rounded-xl border border-slate-800 w-full h-32 object-cover' />"
                    )
                cards.append(
                    "<div class='glass-premium p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3'>"
                    f"<div class='flex items-center justify-between gap-3'><p class='text-sm font-semibold text-white'>{self._escape(title)}</p>{link_html}</div>"
                    f"{image_html}"
                    f"<p class='text-sm text-slate-300 leading-relaxed'>{self._escape(summary)}</p>"
                    "</div>"
                )
            return "<div class='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6'>" + "".join(cards) + "</div>"

        def render_diagnostics(items):
            if not items:
                return "<div class='text-slate-500 text-sm italic'>No diagnostics available.</div>"
            rows = []
            for item in items:
                rows.append(
                    "<div class='flex items-center justify-between border-b border-slate-800/70 py-2'>"
                    f"<span class='text-xs text-slate-400'>{self._escape(item.get('label'))}</span>"
                    f"<span class='text-xs text-slate-200'>{self._escape(item.get('value'))}</span>"
                    "</div>"
                )
            return "<div class='space-y-1'>" + "".join(rows) + "</div>"

        return (
            "<div class='min-h-screen p-6 space-y-8 font-sans text-slate-200 bg-slate-950'>"
            "<div class='glass-premium p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4'>"
            "<div class='flex flex-wrap items-center justify-between gap-4'>"
            "<div>"
            f"<p class='text-xs uppercase tracking-[0.3em] text-slate-500'>{self._escape(subtitle)}</p>"
            f"<h1 class='text-3xl md:text-4xl font-semibold text-white'>{self._escape(system_name)} Intelligence Command</h1>"
            f"<p class='text-sm text-slate-400 mt-2'>{self._escape(location)} · Updated {self._escape(updated_at)}</p>"
            "</div>"
            "<div class='flex items-center gap-3'>"
            f"<span class='px-3 py-1 rounded-full text-xs uppercase tracking-wider bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'>System Online</span>"
            f"<span class='px-3 py-1 rounded-full text-xs uppercase tracking-wider bg-cyan-500/10 text-cyan-300 border border-cyan-500/30'>Cache {self._escape(cache_status)}</span>"
            "</div>"
            "</div>"
            f"{render_hero(hero)}"
            "</div>"

            "<div class='grid grid-cols-1 xl:grid-cols-3 gap-6'>"
            "<div class='xl:col-span-2 space-y-6'>"
            "<div class='glass-premium p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4'>"
            "<h2 class='text-sm uppercase tracking-widest text-slate-400 font-semibold'>Visual Intelligence</h2>"
            f"{render_visuals(visuals)}"
            "</div>"
            "<div class='glass-premium p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4'>"
            "<h2 class='text-sm uppercase tracking-widest text-slate-400 font-semibold'>Environmental Breakdown</h2>"
            "<div class='space-y-4'>"
            "<div>"
            "<p class='text-xs uppercase tracking-wider text-slate-500 mb-2'>Atmosphere</p>"
            f"{render_metric_cards(atmosphere)}"
            "</div>"
            "<div>"
            "<p class='text-xs uppercase tracking-wider text-slate-500 mb-2'>Soil Intelligence</p>"
            f"{render_metric_cards(soil)}"
            "</div>"
            "<div>"
            "<p class='text-xs uppercase tracking-wider text-slate-500 mb-2'>Weather Events</p>"
            f"{render_metric_cards(weather)}"
            "</div>"
            "</div>"
            "</div>"
            "</div>"
            "<div class='space-y-6'>"
            "<div class='glass-premium p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4'>"
            "<h2 class='text-sm uppercase tracking-widest text-slate-400 font-semibold'>Waste Risk Assessment</h2>"
            f"{render_risks(risks)}"
            "</div>"
            "<div class='glass-premium p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4'>"
            "<h2 class='text-sm uppercase tracking-widest text-slate-400 font-semibold'>AI Strategic Recommendations</h2>"
            f"{render_insights(insights)}"
            "</div>"
            "</div>"
            "</div>"

            "<div class='glass-premium p-6 rounded-3xl border border-slate-800 shadow-xl space-y-4'>"
            "<h2 class='text-sm uppercase tracking-widest text-slate-400 font-semibold'>Latest Environmental Intelligence</h2>"
            f"{render_research(research)}"
            "</div>"

            "<details class='glass-premium p-6 rounded-3xl border border-slate-800 shadow-xl'>"
            "<summary class='text-sm uppercase tracking-widest text-slate-400 cursor-pointer'>Advanced Diagnostics</summary>"
            f"<div class='mt-4'>{render_diagnostics(diagnostics)}</div>"
            "</details>"

            "<div class='flex justify-end'>"
            "<button onclick='window.close()' class='px-4 py-2 text-xs uppercase tracking-tighter bg-slate-800 hover:bg-red-900/40 border border-slate-700 transition-all duration-300 rounded-md text-slate-300'>Close Dashboard</button>"
            "</div>"
            "</div>"
        )

    def generate_dashboard(self, data_json):
        """Transforms agent data into a high-end HTML dashboard (deterministic, no LLM)."""
        print("🎨 Orchestrating real-time data into luxury dashboard...")

        payload = data_json
        if isinstance(data_json, list):
            payload = {"items": data_json}

        if not isinstance(payload, dict):
            payload = {"items": [str(payload)]}

        html_content = self._render_dashboard_body(payload)

        base_html = self._read_base_template()
        if not base_html:
            return False

        final_html = (
            base_html
            .replace("{{CONTENT}}", html_content)
            .replace("{{DASHBOARD_BODY}}", html_content)
            .replace("{{SYSTEM_NAME}}", self._escape(self.system_name))
        )

        try:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(final_html)
            return True
        except Exception as e:
            print(f"Error generating dashboard: {e}")
            return False

    def open_dashboard(self):
        """Opens the generated dashboard in a new window."""
        path = os.path.abspath(self.output_file)
        if not self._opened:
            webbrowser.open(f"file://{path}", new=0, autoraise=False)
            self._opened = True
            print(f"🚀 Dashboard opened: {path}")

    def close_dashboard(self):
        print("ℹ️ Please use the 'Close Dashboard' button within the browser window.")
