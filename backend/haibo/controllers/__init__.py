from haibo.controllers.admin_controller import bp as admin_bp
from haibo.controllers.fixed_expense_controller import bp as fixed_bp
from haibo.controllers.health_controller import bp as health_bp
from haibo.controllers.monthly_controller import bp as monthly_bp
from haibo.controllers.report_controller import bp as report_bp


def register_controllers(app):
    app.register_blueprint(health_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(fixed_bp)
    app.register_blueprint(monthly_bp)
    app.register_blueprint(report_bp)
