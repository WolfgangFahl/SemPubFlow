import datetime
from typing import Optional

from sempubflow.models.proceedings import Proceedings
from sempubflow.models.scholar import Scholar


class CeurVolumePage:
    """
    Renders a Ceur volume page
    """

    def __init__(self, proceedings: Proceedings):
        self.proceedings = proceedings

    def render(self) -> str:
        vol_number = "XXXX"
        vol_number_text = f"Vol-{vol_number}"
        event = self.proceedings.event[0] if self.proceedings.event else None
        editors = "\n".join([self._render_editor(editor) for editor in self.proceedings.editor])
        html = f"""<iframe style="width: 100vw; height:100vh "
    srcdoc='
<!doctype html>
<html
    lang="en"
    prefix="bibo: http://purl.org/ontology/bibo/
          event: http://purl.org/NET/c4dm/event.owl#
          time: http://www.w3.org/2006/time#
          swc: http://data.semanticweb.org/ns/swc/ontology#
          xsd: http://www.w3.org/2001/XMLSchema#"
    typeof="bibo:Proceedings">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, user-scalable=no, initial-scale=1.0, maximum-scale=1.0, minimum-scale=1.0">
    <meta http-equiv="X-UA-Compatible" content="ie=edge">
    <link rel="stylesheet" type="text/css" href="https://ceur-ws.org/ceur-ws.css">
    <link rel="stylesheet" type="text/css" href="https://ceur-ws.org/ceur-ws-semantic.css"/>
    <link rel="foaf:page" href="{ "https://ceur-ws.org/" + vol_number_text}"/>
    <title>CEUR-WS.org/{vol_number_text} - { self.proceedings.title } ({self.proceedings.event[0].acronym if self.proceedings.event else ""})</title>
</head>
<body>

<table style="border: 0; border-spacing: 0; border-collapse: collapse; width: 95%">
        <tbody>
            <tr>
                <td style="text-align: left; vertical-align: middle">
                    <a rel="dcterms:partOf" href="http://ceur-ws.org/">
                        <div id="CEURWSLOGO"></div>
                    </a>
                 </td>
                <td style="text-align: right; vertical-align: middle">

                    <span property="bibo:volume" datatype="xsd:nonNegativeInteger" content="{vol_number}" class="CEURVOLNR">{vol_number_text}</span> <br/>&#xa;
                    <span property="bibo:uri dcterms:identifier" class="CEURURN">urn:nbn:de:0074-{vol_number}-C</span>
                    <p class="unobtrusive copyright" style="text-align: justify">Copyright ©
                    <span class="CEURPUBYEAR">{self.proceedings.publication_date}</span> for the individual papers
                    by the papers authors. Copying permitted for private and academic purposes.
                    This volume is published and copyrighted by its editors.</p>

                </td>
            </tr>
        </tbody>
    </table>
    <hr/>

    <br/><br/><br/>&#xa;
    
    <h1>
        <a rel="foaf:homepage" href="{self.proceedings.event[0].official_website if self.proceedings.event else ""}">
            <span about="" property="bibo:shortTitle" class="CEURVOLACRONYM">{ self.proceedings.event[0].acronym if self.proceedings.event else ""} { self.proceedings.publication_date.year if self.proceedings.publication_date else ""}</span>
        </a>
        <br/>&#xa;
      <span property="dcterms:alternative" class="CEURVOLTITLE">{self.proceedings.title}</span>
    </h1>
    
     <br/>
    <h3>
        <span property="dcterms:title" class="CEURFULLTITLE">{self.proceedings.title}</span><br/>&#xa;
    </h3>
    <h3>
        <span rel="bibo:presentedAt" typeof="bibo:Workshop" class="CEURLOCTIME">
            <span rel="event:place" resource="https://www.wikidata.org/location">
                { self.proceedings.event[0].get_full_location() if self.proceedings.event else "" }
            </span>,
            {self._format_date_range(event.start_time, event.end_time) if event else ""}
        </span>.
    </h3>
    <br/>&#xa;
    
    <b> Edited by </b>
    <p>

    </p>
    <h3 rel="bibo:editor">
        {editors}
    </h3>

    <hr/>

    <br/><br/><br/>&#xa;


</body>
</html>'>
</iframe>
        """
        return html

    def _render_editor(self, scholar: Scholar) -> str:
        html = ""
        if scholar.official_website:
            html += f"""
            <a href="{scholar.official_website}">
                <span property="foaf:name" class="CEURVOLEDITOR">
                    {scholar.name}
                </span>
            </a>
            """
        else:
            html += f"""
            <span about="_:{ scholar.wikidata_id }" property="foaf:name" class="CEURVOLEDITOR">
                {scholar.name}
            </span>
            """
        if scholar.affiliation:
            html += f""", {scholar.affiliation[0].name}, {scholar.affiliation[0].country}<br/>&#xa;"""
        return html

    def _format_date_range(self, start_date: datetime.datetime, end_date: Optional[datetime.datetime]) -> str:
        html = ""
        if start_date and end_date:
            if start_date.year == end_date.year:
                start_date_value = start_date.strftime("%B %d")
            else:
                start_date_value = start_date.isoformat()
            if start_date.year == end_date.year and start_date.month == end_date.month:
                end_date_value = end_date.strftime("%d, %Y")
            else:
                end_date_value = end_date.strftime("%B %d, %Y")
            html = f"""
            <span rel="event:time">
                    <span rel="time:hasBeginning">
                        <span property="time:inXSDDateTime" content="{start_date}" datatype="xsd:date">
                            {start_date_value}
                        </span>
                    </span>
                    to
                    <span rel="time:hasEnd">
                        <span property="time:inXSDDateTime" content="{{ volume.date_to }}" datatype="xsd:date">
                            {end_date_value}
                        </span>
                    </span>
                </span>
            """
        elif start_date:
            html = f"""<span property="dcterms:date" content="{start_date.isoformat()}" datatype="xsd:date">{start_date.isoformat()}</span>"""
        else:
            pass
        return html

