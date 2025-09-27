from flask import Blueprint, request, jsonify, current_app
from .extensions import db
from .models import Template, TemplateVariable, Generation
from flask_jwt_extended import jwt_required, get_jwt_identity
from .render_util import safe_render, find_undeclared_vars
import json

bp = Blueprint("templates", __name__, url_prefix="/api/templates")

@bp.route("", methods=["GET"])
def list_templates():
    # simple list, add pagination/filters as needed
    templates = Template.query.all()
    out = []
    for t in templates:
        out.append({
            "id": t.id,
            "name": t.name,
            "slug": t.slug,
            "description": t.description,
            "owner_id": t.owner_id,
            "is_public": t.is_public,
            "created_at": t.created_at.isoformat()
        })
    return jsonify(out)

@bp.route("", methods=["POST"])
@jwt_required()
def create_template():
    data = request.get_json(force=True)
    name = data.get("name")
    slug = data.get("slug")
    content = data.get("content", "")
    description = data.get("description")
    variables = data.get("variables", [])
    if not name or not slug or not content:
        return jsonify({"msg":"name, slug, content required"}), 400
    if Template.query.filter_by(slug=slug).first():
        return jsonify({"msg":"slug exists"}), 400
    # get_jwt_identity returns a string (user id) after auth fix
    identity = get_jwt_identity()
    owner_id = int(identity) if identity is not None else None
    t = Template(name=name, slug=slug, content=content, description=description, owner_id=owner_id)
    db.session.add(t)
    db.session.flush()

    # optional variables
    try:
        for v in variables or []:
            tv = TemplateVariable(
                template_id=t.id,
                name=v.get("name"),
                type=v.get("type") or "string",
                default_value=(
                    json.dumps(v.get("default"), ensure_ascii=False)
                    if (v.get("type") == "json" and v.get("default") is not None)
                    else v.get("default")
                ),
                required=bool(v.get("required", False)),
                options=(None if v.get("options") is None else json.dumps(v.get("options"), ensure_ascii=False)),
                description=v.get("description"),
            )
            db.session.add(tv)
    except Exception:
        db.session.rollback()
        return jsonify({"msg": "invalid variables"}), 400

    db.session.commit()
    return jsonify({"id": t.id}), 201

@bp.route("/<int:tid>", methods=["GET"])
def get_template(tid):
    t = Template.query.get_or_404(tid)
    vars_q = []
    for v in t.variables:
        try:
            opts = v.options_json()
        except:
            opts = None
        # parse default by type
        default_val = v.default_value
        if v.type == 'number':
            try:
                default_val = float(default_val) if default_val is not None else None
            except Exception:
                pass
        elif v.type == 'boolean':
            if isinstance(default_val, str):
                default_val = default_val.lower() in ('1','true','yes','on')
        elif v.type == 'json':
            try:
                default_val = json.loads(default_val) if default_val else None
            except Exception:
                default_val = None
        vars_q.append({
            "id": v.id,
            "name": v.name,
            "type": v.type,
            "default": default_val,
            "required": v.required,
            "options": opts,
            "description": v.description
        })
    return jsonify({
        "id": t.id,
        "name": t.name,
        "slug": t.slug,
        "description": t.description,
        "content": t.content,
        "variables": vars_q
    })

@bp.route("/<int:tid>", methods=["PUT"])
@jwt_required()
def update_template(tid):
    t = Template.query.get_or_404(tid)
    data = request.get_json(force=True)
    t.name = data.get("name", t.name)
    t.slug = data.get("slug", t.slug)
    t.description = data.get("description", t.description)
    t.content = data.get("content", t.content)
    # replace variables if provided
    if "variables" in data:
        vars_in = data.get("variables") or []
        # delete existing
        for old in list(t.variables):
            db.session.delete(old)
        try:
            for v in vars_in:
                tv = TemplateVariable(
                    template_id=t.id,
                    name=v.get("name"),
                    type=v.get("type") or "string",
                    default_value=(
                        json.dumps(v.get("default"), ensure_ascii=False)
                        if (v.get("type") == "json" and v.get("default") is not None)
                        else v.get("default")
                    ),
                    required=bool(v.get("required", False)),
                    options=(None if v.get("options") is None else json.dumps(v.get("options"), ensure_ascii=False)),
                    description=v.get("description"),
                )
                db.session.add(tv)
        except Exception:
            db.session.rollback()
            return jsonify({"msg": "invalid variables"}), 400
    db.session.commit()
    return jsonify({"msg":"updated"})

@bp.route("/<int:tid>", methods=["DELETE"])
@jwt_required()
def delete_template(tid):
    t = Template.query.get_or_404(tid)
    db.session.delete(t)
    db.session.commit()
    return jsonify({"msg":"deleted"})

@bp.route("/<int:tid>/render", methods=["POST"])
def render_template(tid):
    """
    Body JSON: { values: { var1: val1, var2: val2, ... }, save: true|false }
    """
    t = Template.query.get_or_404(tid)
    payload = request.get_json(force=True) or {}
    values = payload.get("values", {})
    # optional: validate values against TemplateVariable declarations
    try:
        preview = safe_render(t.content, values)
    except Exception as e:
        return jsonify({"msg":"render error", "detail": str(e)}), 400

    # save generation record (non-auth user can still create)
    gen = Generation(template_id=t.id, user_id=None, input_values=json.dumps(values, ensure_ascii=False), output_preview=preview)
    db.session.add(gen)
    db.session.commit()

    return jsonify({"preview": preview, "generation_id": gen.id})
