from flask import Blueprint, render_template, request, Response, request

voice_bp = Blueprint(
    'voice',
    __name__
)

@voice_bp.route("/voice", methods=["GET", "POST"])
def voice():
    return Response("""
<Response>
    <Say voice="alice" language="es-ES">
        Hola, estás siendo atendido por el asistente virtual.
    </Say>
</Response>
""", mimetype='text/xml')