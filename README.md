# Water Jump Platformer

A Pygame-based platformer game where players jump over water pools while avoiding obstacles and collecting points.

This game features a player character who must navigate through a series of water pools and obstacles. The game incorporates dynamic asset management, level progression, and various gameplay elements to create an engaging experience.

## Repository Structure

```
.
├── asset_manager_optimized.py
├── asset_manager.py
├── main.py
└── requirements.txt
```

### Key Files:

- `main.py`: The main entry point for the game, containing the core game loop and initialization.
- `asset_manager_optimized.py`: An optimized version of the asset manager for efficient asset handling.
- `asset_manager.py`: Manages game assets, including downloading and caching from an S3 bucket.
- `requirements.txt`: Lists all the Python dependencies required for the project.

## Usage Instructions

### Installation

1. Ensure you have Python 3.7+ installed on your system.
2. Clone the repository to your local machine.
3. Navigate to the project directory in your terminal.
4. Install the required dependencies using pip:
   ```
   pip install -r requirements.txt
   ```

### Configuration

1. Create a `.env` file in the project root with the following content:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_REGION=your_region
   S3_BUCKET_NAME=your_bucket_name
   ```
   Replace the placeholders with your actual AWS credentials and S3 bucket information.

### Running the Game

1. Navigate to the project directory in your terminal.
2. Run the game using:
   ```
   python main.py
   ```

### Gameplay

- Use the left and right arrow keys to move the player.
- Press the spacebar to jump over water pools and obstacles.
- Avoid falling into water pools to maintain lives.
- Progress through levels by covering a certain distance.

### Troubleshooting

1. Asset Loading Issues:
   - If you encounter "Couldn't load some images" or "Couldn't load some sounds" messages:
     - Ensure that your AWS credentials and S3 bucket information in the `.env` file are correct.
     - Check your internet connection to ensure the game can access the S3 bucket.
   - If issues persist, the game will use fallback shapes and disable sounds.

2. S3 Connection Problems:
   - If you see "S3 connection failed" or "Failed to load assets from S3":
     - Check your internet connection.
     - Verify that the AWS credentials in your `.env` file are correct.
     - Ensure that the specified S3 bucket exists and is accessible.
   - The game will fall back to local assets if S3 connection fails.

3. Performance Issues:
   - If the game is running slowly:
     - Close other resource-intensive applications.
     - Reduce the game window size or lower the resolution in `main.py`.
   - Monitor system resources to identify potential bottlenecks.

## Data Flow

The Water Jump Platformer game follows this data flow:

1. Initialization:
   - Pygame is initialized
   - Game assets are loaded from S3 bucket
   - Game state and player are created

2. Game Loop:
   - Handle user input (keyboard events)
   - Update game state (player position, obstacles, score)
   - Check for collisions
   - Render game elements
   - Update display

3. Asset Management:
   - GameAssetManager checks S3 for assets
   - Downloads and caches assets locally
   - Provides assets to the game as needed

4. Level Progression:
   - Track distance covered
   - Trigger level transitions
   - Adjust game difficulty

```
[Initialization] -> [Asset Loading] -> [Game Loop] -> [Render] -> [Update State]
                                          ^                          |
                                          |                          |
                                          +--- [Handle Input] <------+
```

## Infrastructure

The game utilizes AWS S3 for asset storage and management. Key infrastructure components include:

- S3 Bucket:
  - Type: AWS::S3::Bucket
  - Purpose: Stores game assets (images, sounds)

- IAM Role:
  - Type: AWS::IAM::Role
  - Purpose: Provides necessary permissions for the game to access the S3 bucket

### Future Plans

The game is planned to incorporate additional AWS services to enhance its functionality:

1. CloudFront Integration:
   - The game assets will be hosted on CloudFront for improved global distribution and lower latency.

2. User Authentication:
   - A login screen will be implemented using Amazon Cognito for user management and authentication.

3. Notification Service:
   - Amazon Simple Notification Service (SNS) will be integrated to send email notifications to users for various game events or updates.

These future enhancements will improve the game's scalability, user management, and communication capabilities.