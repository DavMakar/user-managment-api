import os
import sys
from app.main import logger, init_message_broker, start_rabbitmq_consumer, app
from app.main import rabbitmq_connected

if __name__ == '__main__':
    try:
        logger.info("=" * 50)
        logger.info("STARTING APPLICATION")
        logger.info("=" * 50)
        
        # Initialize RabbitMQ with retries
        init_message_broker()

        # Start RabbitMQ consumer in background (only if connected)
        if rabbitmq_connected:
            logger.info("Starting RabbitMQ consumer...")
            consumer_started = start_rabbitmq_consumer()
            if consumer_started:
                logger.info("✓ RabbitMQ consumer started")
            else:
                logger.warning("⚠ RabbitMQ consumer failed to start")
        else:
            logger.warning("⚠ RabbitMQ not connected, skipping consumer startup")

        # Get Flask config
        port = int(os.getenv('FLASK_PORT', 5000))
        debug = os.getenv('FLASK_ENV') == 'development'

        logger.info(f"✓ Starting Flask app on port {port}")
        logger.info(f"  Debug mode: {debug}")
        logger.info("=" * 50)
        
        # Disable Flask's debug reloader for cleaner startup
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug,
            use_reloader=False  # Disable auto-reload to prevent double initialization
        )

    except KeyboardInterrupt:
        logger.info("Application interrupted")
        sys.exit(0)
    except Exception as e:
        logger.error(f"✗ Application error: {e}", exc_info=True)
        sys.exit(1)