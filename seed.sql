-- Student Wellness Companion (Wellvia) Initial Seed Data

USE `wellness_db`;

-- 1. Default Achievements / Badges
INSERT INTO `achievements` (`name`, `description`, `badge_icon`, `criteria_type`, `criteria_value`) VALUES
('3-Day Streak', 'Logged daily wellness activities for 3 consecutive days.', 'fire', 'streak', 3),
('7-Day Streak', 'Maintained consistency for 7 consecutive days!', 'flame-fill', 'streak', 7),
('30-Day Streak', 'Exceptional habit consistency for 30 days!', 'trophy-fill', 'streak', 30),
('Hydration Hero', 'Met daily hydration targets for 7 consecutive days.', 'droplet-fill', 'hydration_streak', 7),
('Early Sleeper', 'Recorded 7+ hours of restful sleep for 5 days.', 'moon-stars-fill', 'sleep_count', 5),
('Active Student', 'Completed exercise sessions 7 times in a month.', 'activity', 'exercise_count', 7),
('Challenge Conqueror', 'Successfully completed 10 wellness challenges.', 'award-fill', 'challenges_completed', 10),
('Wellness Explorer', 'Logged all 6 wellness categories in a single day.', 'compass-fill', 'all_categories_day', 1);

-- 2. Default Curated Wellness Tips
INSERT INTO `wellness_tips` (`category`, `content`, `is_active`) VALUES
('Sleep', 'Aim for 7–9 hours of sleep each night. Establish a calming pre-bedtime routine and turn off blue-light screens 30 minutes before sleep.', 1),
('Sleep', 'Maintain a consistent sleep schedule even on weekends to reinforce your natural circadian rhythm.', 1),
('Hydration', 'Drink at least 8 glasses (approx. 2 liters) of water daily. Keep a reusable water bottle at your study desk.', 1),
('Hydration', 'Hydrate first thing in the morning to kickstart your metabolism and boost alertness.', 1),
('Exercise', 'Take a 15-minute brisk walk between long study sessions. Regular physical movement improves focus and reduces stress.', 1),
('Exercise', 'Incorporate gentle stretching or yoga during study breaks to relieve muscle tension in your neck and back.', 1),
('Stress', 'Try the 4-7-8 breathing technique during stressful moments: inhale for 4 seconds, hold for 7 seconds, exhale for 8 seconds.', 1),
('Stress', 'Break large academic tasks into smaller 25-minute Pomodoro study intervals with short breaks to prevent burnout.', 1),
('Study', 'Create a dedicated, clutter-free study environment to mentally separate work time from relaxation.', 1),
('Study', 'Review complex notes right before sleep to enhance memory consolidation during deep sleep cycles.', 1),
('General', 'Take time every evening to reflect on positive events and accomplishments from your day.', 1);

-- 3. Default Initial Challenges
INSERT INTO `challenges` (`title`, `description`, `challenge_type`, `points`, `is_active`) VALUES
('Hydration Boost', 'Drink at least 8 glasses of water throughout the day.', 'daily', 20, 1),
('Study Break Stretches', 'Take a 10-minute stretching break during your study sessions today.', 'daily', 20, 1),
('8-Hour Sleep Night', 'Get 8 hours of restorative sleep tonight.', 'daily', 20, 1),
('Screen-Free Bedtime', 'Avoid using phones or computers 30 minutes before going to bed.', 'daily', 20, 1),
('Weekly Exercise Master', 'Complete at least 3 exercise sessions this week (minimum 20 mins each).', 'weekly', 50, 1),
('Consistent Habit Tracker', 'Log your wellness data every day this week.', 'weekly', 50, 1);
