"""
Robot API - FastAPI endpoints
==============================

API RESTful para control de robots mediante chat y comandos directos.
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from ..config.robot_config import RobotConfig
from ..core.robot import RobotMovementEngine
from ..chat.chat_controller import ChatRobotController
from ..core.exceptions import (
    RobotMovementError,
    TrajectoryError,
    IKError,
    RobotConnectionError,
    RobotNotConnectedError,
    RobotMovementInProgressError
)
from .metrics_api import router as metrics_router
from .resources_api import router as resources_router
from .system_api import router as system_router
from .analytics_api import router as analytics_router
from .tasks_api import router as tasks_router
from .notifications_api import router as notifications_router
from .monitoring_api import router as monitoring_router
from .export_api import router as export_router
from .security_api import router as security_router
from .reports_api import router as reports_router
from .dashboards_api import router as dashboards_router
from .features_api import router as features_router
from .knowledge_api import router as knowledge_router
from .collaboration_api import router as collaboration_router
from .version_api import router as version_router
from .webhook_api import router as webhook_router
from .graphql_api import router as graphql_router
from .streaming_api import router as streaming_router
from .cache_api import router as cache_router
from .load_balancer_api import router as load_balancer_router
from .service_api import router as service_router
from .queue_api import router as queue_router
from .rate_limit_api import router as rate_limit_router
from .retry_api import router as retry_router
from .health_api import router as health_router
from .resource_api import router as resource_router
from .observability_api import router as observability_router
from .distributed_api import router as distributed_router
from .task_api import router as task_router
from .pattern_api import router as pattern_router
from .microservices_api import router as microservices_router
from .data_sync_api import router as data_sync_router
from .deep_learning_api import router as deep_learning_router
from .llm_api import router as llm_router
from .universal_robot_api import router as universal_robot_router

logger = logging.getLogger(__name__)


# Pydantic models
class MoveToRequest(BaseModel):
    """Request para mover a posición."""
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    z: float = Field(..., description="Z coordinate")
    orientation: Optional[List[float]] = Field(None, description="Orientation quaternion [qx, qy, qz, qw]")


class ChatMessage(BaseModel):
    """Mensaje de chat."""
    message: str = Field(..., description="Chat message or command")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")


class ChatResponse(BaseModel):
    """Respuesta de chat."""
    success: bool
    message: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class WaypointRequest(BaseModel):
    """Request para waypoint."""
    x: float
    y: float
    z: float
    orientation: Optional[List[float]] = None


class PathRequest(BaseModel):
    """Request para ruta con múltiples waypoints."""
    waypoints: List[WaypointRequest]


class ObstaclesRequest(BaseModel):
    """Request para actualizar obstáculos."""
    obstacles: List[List[float]]  # Cada obstáculo: [min_x, min_y, min_z, max_x, max_y, max_z]


def create_robot_app(config: RobotConfig) -> FastAPI:
    """Crear aplicación FastAPI."""
    app = FastAPI(
        title="Robot Movement AI API",
        description="Plataforma IA de Movimiento Robótico - Control mediante chat",
        version="1.0.0"
    )
    
    # CORS
    if config.api_cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.api_cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Inicializar componentes
    movement_engine = RobotMovementEngine(config)
    chat_controller = ChatRobotController(movement_engine, config)
    
    # Estado global (en producción usaría dependency injection)
    app.state.movement_engine = movement_engine
    app.state.chat_controller = chat_controller
    app.state.config = config
    app.state.initialized = False
    
    # Incluir routers
    app.include_router(metrics_router)
    app.include_router(resources_router)
    app.include_router(system_router)
    app.include_router(analytics_router)
    app.include_router(tasks_router)
    app.include_router(notifications_router)
    app.include_router(monitoring_router)
    app.include_router(export_router)
    app.include_router(security_router)
    app.include_router(reports_router)
    app.include_router(dashboards_router)
    app.include_router(features_router)
    app.include_router(knowledge_router)
    app.include_router(collaboration_router)
    app.include_router(version_router)
    app.include_router(webhook_router)
    app.include_router(graphql_router)
    app.include_router(streaming_router)
    app.include_router(cache_router)
    app.include_router(load_balancer_router)
    app.include_router(service_router)
    app.include_router(queue_router)
    app.include_router(rate_limit_router)
    app.include_router(retry_router)
    app.include_router(health_router)
    app.include_router(resource_router)
    app.include_router(observability_router)
    app.include_router(distributed_router)
    app.include_router(task_router)
    app.include_router(pattern_router)
    app.include_router(microservices_router)
    app.include_router(data_sync_router)
    app.include_router(deep_learning_router)
    app.include_router(llm_router)
    app.include_router(universal_robot_router)
    
    @app.on_event("startup")
    async def startup():
        """Inicializar al arrancar."""
        try:
            await movement_engine.initialize()
            app.state.initialized = True
            logger.info("API started and robot initialized")
        except Exception as e:
            logger.error(f"Failed to initialize robot: {e}")
            app.state.initialized = False
            raise
    
    @app.on_event("shutdown")
    async def shutdown():
        """Limpiar al apagar."""
        await movement_engine.shutdown()
        logger.info("API shut down")
    
    @app.get("/")
    async def root():
        """Endpoint raíz."""
        return {
            "name": "Robot Movement AI API",
            "version": "1.0.0",
            "status": "running",
            "robot_brand": config.robot_brand.value,
            "ros_enabled": config.ros_enabled
        }
    
    @app.get("/health")
    async def health():
        """Health check mejorado."""
        from ..core.health_check import get_health_check_system
        
        health_system = get_health_check_system()
        health_report = health_system.get_health_report()
        
        # Agregar información adicional
        status = movement_engine.get_status()
        feedback_stats = movement_engine.feedback_system.get_statistics()
        
        health_report["robot"] = {
            "initialized": app.state.initialized,
            "status": status,
            "feedback_stats": feedback_stats
        }
        
        return health_report
    
    @app.post("/api/v1/move/to", response_model=Dict[str, Any])
    async def move_to(request: MoveToRequest):
        """Mover robot a posición absoluta."""
        if not app.state.initialized:
            raise HTTPException(status_code=503, detail="Robot not initialized")
        
        try:
            orientation = None
            if request.orientation:
                import numpy as np
                orientation = np.array(request.orientation)
            
            from ..core.inverse_kinematics import EndEffectorPose
            target_pose = EndEffectorPose(
                position=[request.x, request.y, request.z],
                orientation=orientation or [0.0, 0.0, 0.0, 1.0]
            )
            
            success = await movement_engine.move_to_pose(target_pose)
            
            return {
                "success": success,
                "message": f"Moving to ({request.x}, {request.y}, {request.z})",
                "target": {"x": request.x, "y": request.y, "z": request.z}
            }
        except RobotNotConnectedError as e:
            raise HTTPException(status_code=503, detail=str(e))
        except RobotMovementInProgressError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except TrajectoryError as e:
            raise HTTPException(status_code=400, detail=f"Trajectory error: {e}")
        except IKError as e:
            raise HTTPException(status_code=400, detail=f"IK error: {e}")
        except RobotMovementError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in move_to: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @app.post("/api/v1/chat", response_model=ChatResponse)
    async def chat(message: ChatMessage):
        """Procesar mensaje de chat."""
        try:
            result = await chat_controller.process_chat_message(
                message.message,
                message.context
            )
            return ChatResponse(**result)
        except Exception as e:
            logger.error(f"Error in chat: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/stop")
    async def stop():
        """Detener movimiento del robot."""
        try:
            await movement_engine.stop_movement()
            return {
                "success": True,
                "message": "Robot stopped"
            }
        except Exception as e:
            logger.error(f"Error in stop: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/status")
    async def status():
        """Obtener estado del robot."""
        try:
            robot_status = movement_engine.get_status()
            feedback_stats = movement_engine.feedback_system.get_statistics()
            
            return {
                "robot_status": robot_status,
                "feedback_stats": feedback_stats,
                "config": config.to_dict()
            }
        except Exception as e:
            logger.error(f"Error in status: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/statistics")
    async def statistics():
        """Obtener estadísticas detalladas del sistema."""
        try:
            engine_stats = movement_engine.get_statistics()
            chat_stats = chat_controller.get_statistics()
            optimizer_stats = movement_engine.trajectory_optimizer.get_statistics()
            
            return {
                "engine_statistics": engine_stats,
                "chat_statistics": chat_stats,
                "optimizer_statistics": optimizer_stats
            }
        except Exception as e:
            logger.error(f"Error in statistics: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/move/path")
    async def move_path(request: PathRequest):
        """Mover robot a lo largo de una ruta con múltiples waypoints."""
        try:
            from ..core.inverse_kinematics import EndEffectorPose
            import numpy as np
            
            waypoints = []
            for wp in request.waypoints:
                orientation = np.array(wp.orientation) if wp.orientation else np.array([0.0, 0.0, 0.0, 1.0])
                waypoints.append(EndEffectorPose(
                    position=np.array([wp.x, wp.y, wp.z]),
                    orientation=orientation
                ))
            
            success = await movement_engine.move_along_path(waypoints)
            
            return {
                "success": success,
                "message": f"Moving along path with {len(waypoints)} waypoints",
                "waypoints_count": len(waypoints)
            }
        except Exception as e:
            logger.error(f"Error in move_path: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/obstacles/update")
    async def update_obstacles(request: ObstaclesRequest):
        """Actualizar lista de obstáculos conocidos."""
        try:
            import numpy as np
            
            obstacles = [np.array(obs) for obs in request.obstacles]
            movement_engine.update_obstacles(obstacles)
            
            return {
                "success": True,
                "message": f"Updated {len(obstacles)} obstacles",
                "obstacles_count": len(obstacles)
            }
        except Exception as e:
            logger.error(f"Error in update_obstacles: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/obstacles")
    async def get_obstacles():
        """Obtener lista de obstáculos conocidos."""
        try:
            obstacles = movement_engine.known_obstacles
            return {
                "obstacles": [obs.tolist() for obs in obstacles],
                "count": len(obstacles)
            }
        except Exception as e:
            logger.error(f"Error in get_obstacles: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/replanification/enable")
    async def enable_replanification(enabled: bool = True):
        """Habilitar/deshabilitar replanificación automática."""
        try:
            movement_engine.replanification_enabled = enabled
            return {
                "success": True,
                "message": f"Replanification {'enabled' if enabled else 'disabled'}",
                "replanification_enabled": enabled
            }
        except Exception as e:
            logger.error(f"Error in enable_replanification: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v1/movement/history")
    async def movement_history(limit: int = 10):
        """Obtener historial de movimientos."""
        try:
            history = movement_engine.movement_history[-limit:]
            return {
                "history": history,
                "total_movements": movement_engine.total_movements,
                "returned_count": len(history)
            }
        except Exception as e:
            logger.error(f"Error in movement_history: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/trajectory/optimize/astar")
    async def optimize_astar(request: MoveToRequest, grid_resolution: float = 0.05):
        """Optimizar trayectoria usando algoritmo A*."""
        try:
            from ..core.trajectory_optimizer import TrajectoryPoint
            from ..core.inverse_kinematics import EndEffectorPose
            import numpy as np
            
            start_feedback = movement_engine.feedback_system.get_latest_feedback()
            if not start_feedback:
                raise HTTPException(status_code=400, detail="No current position available")
            
            start_point = TrajectoryPoint(
                position=start_feedback.end_effector_position,
                orientation=start_feedback.end_effector_orientation,
                timestamp=0.0
            )
            
            orientation = np.array(request.orientation) if request.orientation else np.array([0.0, 0.0, 0.0, 1.0])
            goal_point = TrajectoryPoint(
                position=np.array([request.x, request.y, request.z]),
                orientation=orientation,
                timestamp=0.0
            )
            
            trajectory = movement_engine.trajectory_optimizer.optimize_with_astar(
                start_point, goal_point, movement_engine.known_obstacles, grid_resolution
            )
            
            analysis = movement_engine.trajectory_optimizer.analyze_trajectory(trajectory)
            
            return {
                "success": True,
                "trajectory_points": len(trajectory),
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error in optimize_astar: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/trajectory/optimize/rrt")
    async def optimize_rrt(request: MoveToRequest, max_iterations: int = 1000, step_size: float = 0.1):
        """Optimizar trayectoria usando algoritmo RRT."""
        try:
            from ..core.trajectory_optimizer import TrajectoryPoint
            import numpy as np
            
            start_feedback = movement_engine.feedback_system.get_latest_feedback()
            if not start_feedback:
                raise HTTPException(status_code=400, detail="No current position available")
            
            start_point = TrajectoryPoint(
                position=start_feedback.end_effector_position,
                orientation=start_feedback.end_effector_orientation,
                timestamp=0.0
            )
            
            orientation = np.array(request.orientation) if request.orientation else np.array([0.0, 0.0, 0.0, 1.0])
            goal_point = TrajectoryPoint(
                position=np.array([request.x, request.y, request.z]),
                orientation=orientation,
                timestamp=0.0
            )
            
            trajectory = movement_engine.trajectory_optimizer.optimize_with_rrt(
                start_point, goal_point, movement_engine.known_obstacles, max_iterations, step_size
            )
            
            analysis = movement_engine.trajectory_optimizer.analyze_trajectory(trajectory)
            
            return {
                "success": True,
                "trajectory_points": len(trajectory),
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error in optimize_rrt: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/trajectory/analyze")
    async def analyze_trajectory(request: PathRequest):
        """Analizar trayectoria generada desde waypoints."""
        try:
            from ..core.trajectory_optimizer import TrajectoryPoint
            from ..core.inverse_kinematics import EndEffectorPose
            import numpy as np
            
            if len(request.waypoints) < 2:
                raise HTTPException(status_code=400, detail="Need at least 2 waypoints")
            
            # Generar trayectoria desde waypoints
            trajectory_points = []
            for i, wp in enumerate(request.waypoints):
                orientation = np.array(wp.orientation) if wp.orientation else np.array([0.0, 0.0, 0.0, 1.0])
                point = TrajectoryPoint(
                    position=np.array([wp.x, wp.y, wp.z]),
                    orientation=orientation,
                    timestamp=i * 0.01
                )
                trajectory_points.append(point)
            
            analysis = movement_engine.trajectory_optimizer.analyze_trajectory(trajectory_points)
            
            return {
                "success": True,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"Error in analyze_trajectory: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v1/trajectory/export")
    async def export_trajectory(request: PathRequest, format: str = "json"):
        """Exportar trayectoria a archivo."""
        try:
            from ..core.trajectory_optimizer import TrajectoryPoint
            import numpy as np
            from pathlib import Path
            
            if format not in ["json", "csv"]:
                raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
            
            # Generar trayectoria desde waypoints
            trajectory_points = []
            for i, wp in enumerate(request.waypoints):
                orientation = np.array(wp.orientation) if wp.orientation else np.array([0.0, 0.0, 0.0, 1.0])
                point = TrajectoryPoint(
                    position=np.array([wp.x, wp.y, wp.z]),
                    orientation=orientation,
                    timestamp=i * 0.01
                )
                trajectory_points.append(point)
            
            # Generar nombre de archivo
            filepath = f"trajectory_{int(asyncio.get_event_loop().time())}.{format}"
            filepath = Path(movement_engine.config.storage_path) / filepath
            
            success = movement_engine.trajectory_optimizer.export_trajectory(
                trajectory_points, str(filepath), format
            )
            
            if success:
                return {
                    "success": True,
                    "filepath": str(filepath),
                    "format": format
                }
            else:
                raise HTTPException(status_code=500, detail="Failed to export trajectory")
        except Exception as e:
            logger.error(f"Error in export_trajectory: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.websocket("/ws/chat")
    async def websocket_chat(websocket: WebSocket):
        """WebSocket para chat en tiempo real."""
        await websocket.accept()
        logger.info("WebSocket connection established")
        
        try:
            while True:
                data = await websocket.receive_text()
                
                # Procesar mensaje
                result = await chat_controller.process_chat_message(data)
                
                # Enviar respuesta
                await websocket.send_json(result)
        
        except WebSocketDisconnect:
            logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error in WebSocket: {e}", exc_info=True)
            await websocket.close()
    
    return app


class RobotAPI:
    """Wrapper para la API de robots."""
    
    def __init__(self, config: RobotConfig):
        """Inicializar API."""
        self.config = config
        self.app = create_robot_app(config)
    
    def run(self, host: str = "0.0.0.0", port: int = 8010, reload: bool = False):
        """Ejecutar servidor API."""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            reload=reload,
            log_level=self.config.log_level.lower()
        )

