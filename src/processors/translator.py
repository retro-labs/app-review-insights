import re
from typing import Optional

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except ImportError:
    HAS_TEXTBLOB = False

class ReviewTranslator:
    def __init__(self):
        self._cached_translations = {}
        self._sample_translations = {
            "App crashes on launch after update": "更新后应用启动崩溃",
            "Since updating to version 3.3.0, the app crashes immediately when I try to open it. I've tried restarting my phone and reinstalling the app, but nothing works. This is very frustrating!": "自从更新到3.3.0版本后，我尝试打开应用时立即崩溃。我已经尝试重新启动手机和重新安装应用，但都没有效果。这非常令人沮丧！",
            
            "Great app but crashes during workouts": "很棒的应用但锻炼时崩溃",
            "I love the workout videos and the variety of exercises. However, the app crashes about halfway through every workout. This makes it hard to track my progress.": "我喜欢锻炼视频和多样化的练习。然而，应用在每次锻炼中途都会崩溃。这使得很难跟踪我的进度。",
            
            "Freezes when switching exercises": "切换练习时冻结",
            "The app keeps freezing when I try to switch between different exercises in a workout. Sometimes I have to force quit and start over. Please fix this bug!": "当我尝试在锻炼中切换不同练习时，应用一直冻结。有时我必须强制退出并重新开始。请修复这个bug！",
            
            "Please add dark mode!": "请添加深色模式！",
            "I workout at night and the bright white screen is really hard on my eyes. Adding a dark mode would be a huge improvement. Other fitness apps have this feature.": "我晚上锻炼，明亮的白色屏幕对眼睛非常不好。添加深色模式将是一个巨大的改进。其他健身应用都有这个功能。",
            
            "Apple Watch integration needed": "需要Apple Watch集成",
            "I use my Apple Watch for all my fitness tracking. It would be amazing if the app could sync with Apple Watch to track heart rate, calories, and workout duration automatically.": "我使用Apple Watch进行所有健身追踪。如果应用能够与Apple Watch同步，自动追踪心率、卡路里和锻炼时长，那将太棒了。",
            
            "Add yoga sessions": "添加瑜伽课程",
            "The strength training workouts are great! But I also do yoga and would love to see yoga sessions added to the app. It would make this a complete fitness solution.": "力量训练很棒！但我也做瑜伽，希望看到应用中添加瑜伽课程。这将使其成为一个完整的健身解决方案。",
            
            "Battery drain is terrible": "电池消耗太严重",
            "After using this app for 30 minutes, my phone battery drops by 25%. This is way too much. Other similar apps don't drain the battery nearly as much. Please optimize!": "使用这个应用30分钟后，我的手机电池下降了25%。这太多了。其他类似应用的电池消耗远没有这么多。请优化！",
            
            "App is very slow to load": "应用加载非常慢",
            "The app takes forever to load the workout videos and menus. Sometimes I have to wait 10+ seconds just to navigate to the next screen. This needs to be fixed.": "应用加载锻炼视频和菜单需要很长时间。有时我必须等待10多秒才能导航到下一个屏幕。这需要修复。",
            
            "Lag during video playback": "视频播放时卡顿",
            "The workout videos lag and stutter, especially when I'm doing HIIT workouts. It's hard to follow along when the video keeps pausing. This is a major issue.": "锻炼视频卡顿，尤其是在做HIIT锻炼时。视频不断暂停时很难跟上。这是一个主要问题。",
            
            "UI is confusing": "UI很混乱",
            "I find the user interface really confusing. It's hard to find the workouts I want, and the navigation is not intuitive. A redesign would be very helpful.": "我发现用户界面非常混乱。很难找到我想要的锻炼，导航也不直观。重新设计会非常有帮助。",
            
            "Better progress tracking": "更好的进度跟踪",
            "The progress tracking is basic. I would like to see charts and stats showing my improvement over time. Maybe weekly summaries and achievements.": "进度跟踪很基础。我希望看到图表和统计数据显示我随着时间的进步。也许每周摘要和成就。",
            
            "Subscription is too expensive": "订阅太贵",
            "$19.99/month is way too expensive for what this app offers. I can get similar features from other apps for half the price. I would subscribe if it was cheaper.": "$19.99/月对于这个应用提供的功能来说太贵了。我可以从其他应用以一半的价格获得类似功能。如果便宜些我会订阅。",
            
            "Free version is too limited": "免费版本太有限",
            "The free version only gives you 3 workouts per week. That's not enough to make any progress. You basically have to pay to use the app properly.": "免费版本每周只提供3次锻炼。这不足以取得任何进展。你基本上必须付费才能正常使用应用。",
            
            "Best fitness app ever!": "有史以来最好的健身应用！",
            "I've tried so many fitness apps and this is by far the best. The workouts are challenging but doable, the trainers are great, and I've seen amazing results in just 2 months!": "我尝试过很多健身应用，这是迄今为止最好的。锻炼具有挑战性但可行，教练很棒，我在短短2个月内就看到了惊人的结果！",
            
            "Love the meal planner": "喜欢膳食计划",
            "The meal planner feature is awesome! It helps me stay on track with my diet and the recipes are delicious. This app has everything I need for my fitness journey.": "膳食计划功能太棒了！它帮助我保持饮食计划，食谱也很美味。这个应用拥有我健身之旅所需的一切。",
            
            "Sync issues between devices": "设备间同步问题",
            "My workout history doesn't sync properly between my iPhone and iPad. I completed a workout on my phone but it doesn't show up on my iPad. Very annoying!": "我的锻炼历史在iPhone和iPad之间同步不正常。我在手机上完成了锻炼，但它没有显示在iPad上。非常烦人！",
            
            "Progress not saving": "进度未保存",
            "I completed a 45-minute workout yesterday, but today it shows I only did 0 minutes. My progress isn't being saved properly. This is very discouraging.": "我昨天完成了45分钟的锻炼，但今天显示我只做了0分钟。我的进度保存不正常。这非常令人沮丧。",
            
            "More beginner workouts": "更多初学者锻炼",
            "I'm new to working out and some of the exercises are too hard. I would like to see more beginner-friendly workouts. Maybe a 'getting started' program.": "我刚开始锻炼，有些练习太难了。我希望看到更多适合初学者的锻炼。也许一个'入门'计划。",
            
            "Social features would be great": "社交功能会很棒",
            "It would be fun to connect with friends using the app, share workout achievements, and maybe even compete. A social aspect would make working out more motivating.": "使用应用与朋友连接、分享锻炼成就，甚至竞争会很有趣。社交方面会让锻炼更有动力。",
            
            "Custom workout plans": "自定义锻炼计划",
            "I wish I could create my own custom workout plans instead of just following the pre-made ones. It would be great to select specific exercises and arrange them as I like.": "我希望能够创建自己的自定义锻炼计划，而不仅仅是遵循预制的计划。能够选择特定练习并按我喜欢的方式排列会很棒。",
            
            "Video quality is poor": "视频质量差",
            "The workout videos are often blurry and the audio quality is bad. I can't always hear what the trainer is saying. Please improve the video production quality.": "锻炼视频经常模糊，音频质量也很差。我无法总是听到教练在说什么。请提高视频制作质量。",
            
            "No offline mode": "没有离线模式",
            "I travel a lot and don't always have internet access. It would be great if I could download workouts for offline use. This is a must-have feature.": "我经常旅行，并不总是有互联网接入。如果我可以下载锻炼供离线使用会很棒。这是一个必备功能。",
            
            "Excellent customer support": "出色的客户支持",
            "I had an issue with my subscription and the support team responded within hours. They were very helpful and resolved my issue quickly. Great service!": "我的订阅有问题，支持团队在几小时内就回复了。他们非常有帮助，很快解决了我的问题。很棒的服务！",
            
            "Workout reminders": "锻炼提醒",
            "I often forget to workout. Adding reminders or push notifications would help me stay consistent. Maybe weekly workout reminders based on my schedule.": "我经常忘记锻炼。添加提醒或推送通知会帮助我保持一致。也许基于我的日程安排的每周锻炼提醒。",
            
            "Glitch: sound not working": "故障：声音不工作",
            "The audio doesn't work on some workout videos. I've tried adjusting the volume and restarting the app, but it's still broken. This makes it impossible to follow the workouts.": "某些锻炼视频的音频不工作。我尝试调整音量和重新启动应用，但仍然损坏。这使得无法跟随锻炼。",
            
            "Recovery mode missing": "缺少恢复模式",
            "After intense workouts, I need recovery stretches. It would be great to have a dedicated recovery mode with stretching exercises and foam rolling guides.": "剧烈锻炼后，我需要恢复拉伸。拥有一个专门的恢复模式，包含拉伸练习和泡沫轴指南会很棒。",
            
            "Statistics page is confusing": "统计页面很混乱",
            "The statistics page is hard to understand. I can't easily see my workout history, calories burned, or progress. A cleaner, more organized stats page would be better.": "统计页面很难理解。我无法轻松看到我的锻炼历史、燃烧的卡路里或进度。一个更简洁、更有组织的统计页面会更好。",
            
            "Yearly subscription discount": "年度订阅折扣",
            "I would be happy to pay for a yearly subscription if there was a significant discount. Monthly is too expensive, but a yearly plan at 50% off would be great.": "如果有大幅折扣，我很乐意支付年度订阅。月度太贵了，但50%折扣的年度计划会很棒。",
            
            "Love the challenges!": "喜欢挑战！",
            "The 30-day challenges are awesome! They keep me motivated and I've seen great results. Please add more challenges like a 60-day transformation challenge.": "30天挑战太棒了！它们让我保持动力，我看到了很好的结果。请添加更多挑战，如60天转型挑战。",
            
            "App won't play music": "应用无法播放音乐",
            "When I try to play my own music while working out, the app's audio takes over and my music stops. I want to listen to my own playlist while following the workout.": "当我尝试在锻炼时播放自己的音乐时，应用的音频会接管，我的音乐停止。我想在跟随锻炼时听自己的播放列表。",
            
            "Add meditation sessions": "添加冥想课程",
            "I practice mindfulness meditation daily and would love to see guided meditation sessions added to the app. It would be great for mental health alongside physical fitness.": "我每天练习正念冥想，希望看到应用中添加引导冥想课程。这对心理健康和身体健康都很有好处。",
            
            "Search function broken": "搜索功能损坏",
            "The search bar doesn't work properly. When I search for specific workouts or exercises, it returns no results even though I know they exist in the app.": "搜索栏工作不正常。当我搜索特定锻炼或练习时，即使我知道它们存在于应用中，它也没有返回结果。",
            
            "Timer feature is great": "计时器功能很棒",
            "I love the built-in timer for rest periods between exercises. It helps me keep track of my workout and not waste time. This is a really useful feature!": "我喜欢练习之间休息时间的内置计时器。它帮助我跟踪锻炼，不浪费时间。这是一个非常有用的功能！",
            
            "Profile page needs update": "个人资料页面需要更新",
            "The profile page looks outdated and doesn't show much information. I would like to see more stats, achievements, and customization options for my profile.": "个人资料页面看起来过时了，没有显示太多信息。我希望看到更多统计数据、成就和个人资料的自定义选项。",
            
            "Notifications are annoying": "通知很烦人",
            "I get too many push notifications from this app. Even when I turn them off in settings, I still get some. Can you please fix the notification settings?": "我收到太多来自这个应用的推送通知。即使我在设置中关闭它们，我仍然会收到一些。请修复通知设置好吗？",
            
            "Great for busy people": "非常适合忙碌的人",
            "As a busy mom, I don't have much time for workouts. The 15-minute quick workouts are perfect for me. I can squeeze in a workout during naptime!": "作为一个忙碌的妈妈，我没有太多时间锻炼。15分钟快速锻炼非常适合我。我可以在午睡时间挤出时间锻炼！",
            
            "Bug: cannot share workouts": "Bug：无法分享锻炼",
            "When I try to share my workout progress on social media, the app crashes. I've tried multiple times and it always happens. This feature needs to be fixed.": "当我尝试在社交媒体上分享我的锻炼进度时，应用崩溃。我尝试了多次，总是发生这种情况。这个功能需要修复。",
            
            "Add Pilates workouts": "添加普拉提锻炼",
            "I do Pilates regularly and would love to see more Pilates workouts in the app. The current selection is very limited. Please add more variety!": "我定期做普拉提，希望看到应用中有更多普拉提锻炼。目前的选择非常有限。请添加更多种类！",
            
            "App crashes when trying to purchase": "尝试购买时应用崩溃",
            "When I try to upgrade to the premium version, the app crashes. I've tried on multiple devices and it's the same issue. I want to subscribe but can't!": "当我尝试升级到高级版本时，应用崩溃。我在多个设备上尝试过，都是同样的问题。我想订阅但不能！",
            
            "Best value for money": "性价比最高",
            "After trying many fitness apps, this one offers the best value. The workouts are high quality, the trainers are knowledgeable, and the price is reasonable. Highly recommend!": "尝试了许多健身应用后，这个提供了最好的价值。锻炼质量很高，教练知识渊博，价格合理。强烈推荐！",
            
            "Horrible wouldn't let me cancel my subscription": "太可怕了，不让我取消订阅",
            "I've been trying to cancel my subscription for weeks but the app won't let me. Every time I try to cancel, it redirects me to a blank page. This is terrible customer service!": "我几周来一直在尝试取消订阅，但应用不让我取消。每次我尝试取消，它都会重定向到空白页面。这是糟糕的客户服务！",
            
            "Great app but crashes during workouts": "很棒的应用但锻炼时崩溃",
            "I love the workout videos and the variety of exercises. However, the app crashes about halfway through every workout. This makes it hard to track my progress.": "我喜欢锻炼视频和多样化的练习。然而，应用在每次锻炼中途都会崩溃。这使得很难跟踪我的进度。",
            
            "Freezes when switching exercises": "切换练习时冻结",
            "The app keeps freezing when I try to switch between different exercises in a workout. Sometimes I have to force quit and start over. Please fix this bug!": "当我尝试在锻炼中切换不同练习时，应用一直冻结。有时我必须强制退出并重新开始。请修复这个bug！",
            
            "Battery drain is terrible": "电池消耗太严重",
            "After using this app for 30 minutes, my phone battery drops by 25%. This is way too much. Other similar apps don't drain the battery nearly as much. Please optimize!": "使用这个应用30分钟后，我的手机电池下降了25%。这太多了。其他类似应用的电池消耗远没有这么多。请优化！",
            
            "App is very slow to load": "应用加载非常慢",
            "The app takes forever to load the workout videos and menus. Sometimes I have to wait 10+ seconds just to navigate to the next screen. This needs to be fixed.": "应用加载锻炼视频和菜单需要很长时间。有时我必须等待10多秒才能导航到下一个屏幕。这需要修复。",
            
            "Lag during video playback": "视频播放时卡顿",
            "The workout videos lag and stutter, especially when I'm doing HIIT workouts. It's hard to follow along when the video keeps pausing. This is a major issue.": "锻炼视频卡顿，尤其是在做HIIT锻炼时。视频不断暂停时很难跟上。这是一个主要问题。",
            
            "UI is confusing": "UI很混乱",
            "I find the user interface really confusing. It's hard to find the workouts I want, and the navigation is not intuitive. A redesign would be very helpful.": "我发现用户界面非常混乱。很难找到我想要的锻炼，导航也不直观。重新设计会非常有帮助。",
            
            "Better progress tracking": "更好的进度跟踪",
            "The progress tracking is basic. I would like to see charts and stats showing my improvement over time. Maybe weekly summaries and achievements.": "进度跟踪很基础。我希望看到图表和统计数据显示我随着时间的进步。也许每周摘要和成就。",
            
            "Subscription is too expensive": "订阅太贵",
            "$19.99/month is way too expensive for what this app offers. I can get similar features from other apps for half the price. I would subscribe if it was cheaper.": "$19.99/月对于这个应用提供的功能来说太贵了。我可以从其他应用以一半的价格获得类似功能。如果便宜些我会订阅。",
            
            "Free version is too limited": "免费版本太有限",
            "The free version only gives you 3 workouts per week. That's not enough to make any progress. You basically have to pay to use the app properly.": "免费版本每周只提供3次锻炼。这不足以取得任何进展。你基本上必须付费才能正常使用应用。",
            
            "Sync issues between devices": "设备间同步问题",
            "My workout history doesn't sync properly between my iPhone and iPad. I completed a workout on my phone but it doesn't show up on my iPad. Very annoying!": "我的锻炼历史在iPhone和iPad之间同步不正常。我在手机上完成了锻炼，但它没有显示在iPad上。非常烦人！",
            
            "Progress not saving": "进度未保存",
            "I completed a 45-minute workout yesterday, but today it shows I only did 0 minutes. My progress isn't being saved properly. This is very discouraging.": "我昨天完成了45分钟的锻炼，但今天显示我只做了0分钟。我的进度保存不正常。这非常令人沮丧。",
            
            "More beginner workouts": "更多初学者锻炼",
            "I'm new to working out and some of the exercises are too hard. I would like to see more beginner-friendly workouts. Maybe a 'getting started' program.": "我刚开始锻炼，有些练习太难了。我希望看到更多适合初学者的锻炼。也许一个'入门'计划。",
            
            "Social features would be great": "社交功能会很棒",
            "It would be fun to connect with friends using the app, share workout achievements, and maybe even compete. A social aspect would make working out more motivating.": "使用应用与朋友连接、分享锻炼成就，甚至竞争会很有趣。社交方面会让锻炼更有动力。",
            
            "Custom workout plans": "自定义锻炼计划",
            "I wish I could create my own custom workout plans instead of just following the pre-made ones. It would be great to select specific exercises and arrange them as I like.": "我希望能够创建自己的自定义锻炼计划，而不仅仅是遵循预制的计划。能够选择特定练习并按我喜欢的方式排列会很棒。",
            
            "Video quality is poor": "视频质量差",
            "The workout videos are often blurry and the audio quality is bad. I can't always hear what the trainer is saying. Please improve the video production quality.": "锻炼视频经常模糊，音频质量也很差。我无法总是听到教练在说什么。请提高视频制作质量。",
            
            "No offline mode": "没有离线模式",
            "I travel a lot and don't always have internet access. It would be great if I could download workouts for offline use. This is a must-have feature.": "我经常旅行，并不总是有互联网接入。如果我可以下载锻炼供离线使用会很棒。这是一个必备功能。",
            
            "Workout reminders": "锻炼提醒",
            "I often forget to workout. Adding reminders or push notifications would help me stay consistent. Maybe weekly workout reminders based on my schedule.": "我经常忘记锻炼。添加提醒或推送通知会帮助我保持一致。也许基于我的日程安排的每周锻炼提醒。",
            
            "Glitch: sound not working": "故障：声音不工作",
            "The audio doesn't work on some workout videos. I've tried adjusting the volume and restarting the app, but it's still broken. This makes it impossible to follow the workouts.": "某些锻炼视频的音频不工作。我尝试调整音量和重新启动应用，但仍然损坏。这使得无法跟随锻炼。",
            
            "Recovery mode missing": "缺少恢复模式",
            "After intense workouts, I need recovery stretches. It would be great to have a dedicated recovery mode with stretching exercises and foam rolling guides.": "剧烈锻炼后，我需要恢复拉伸。拥有一个专门的恢复模式，包含拉伸练习和泡沫轴指南会很棒。",
            
            "Statistics page is confusing": "统计页面很混乱",
            "The statistics page is hard to understand. I can't easily see my workout history, calories burned, or progress. A cleaner, more organized stats page would be better.": "统计页面很难理解。我无法轻松看到我的锻炼历史、燃烧的卡路里或进度。一个更简洁、更有组织的统计页面会更好。",
            
            "Yearly subscription discount": "年度订阅折扣",
            "I would be happy to pay for a yearly subscription if there was a significant discount. Monthly is too expensive, but a yearly plan at 50% off would be great.": "如果有大幅折扣，我很乐意支付年度订阅。月度太贵了，但50%折扣的年度计划会很棒。",
            
            "Love the challenges!": "喜欢挑战！",
            "The 30-day challenges are awesome! They keep me motivated and I've seen great results. Please add more challenges like a 60-day transformation challenge.": "30天挑战太棒了！它们让我保持动力，我看到了很好的结果。请添加更多挑战，如60天转型挑战。",
            
            "App won't play music": "应用无法播放音乐",
            "When I try to play my own music while working out, the app's audio takes over and my music stops. I want to listen to my own playlist while following the workout.": "当我尝试在锻炼时播放自己的音乐时，应用的音频会接管，我的音乐停止。我想在跟随锻炼时听自己的播放列表。",
            
            "Add meditation sessions": "添加冥想课程",
            "I practice mindfulness meditation daily and would love to see guided meditation sessions added to the app. It would be great for mental health alongside physical fitness.": "我每天练习正念冥想，希望看到应用中添加引导冥想课程。这对心理健康和身体健康都很有好处。",
            
            "Search function broken": "搜索功能损坏",
            "The search bar doesn't work properly. When I search for specific workouts or exercises, it returns no results even though I know they exist in the app.": "搜索栏工作不正常。当我搜索特定锻炼或练习时，即使我知道它们存在于应用中，它也没有返回结果。",
            
            "Timer feature is great": "计时器功能很棒",
            "I love the built-in timer for rest periods between exercises. It helps me keep track of my workout and not waste time. This is a really useful feature!": "我喜欢练习之间休息时间的内置计时器。它帮助我跟踪锻炼，不浪费时间。这是一个非常有用的功能！",
            
            "Profile page needs update": "个人资料页面需要更新",
            "The profile page looks outdated and doesn't show much information. I would like to see more stats, achievements, and customization options for my profile.": "个人资料页面看起来过时了，没有显示太多信息。我希望看到更多统计数据、成就和个人资料的自定义选项。",
            
            "Notifications are annoying": "通知很烦人",
            "I get too many push notifications from this app. Even when I turn them off in settings, I still get some. Can you please fix the notification settings?": "我收到太多来自这个应用的推送通知。即使我在设置中关闭它们，我仍然会收到一些。请修复通知设置好吗？",
            
            "Great for busy people": "非常适合忙碌的人",
            "As a busy mom, I don't have much time for workouts. The 15-minute quick workouts are perfect for me. I can squeeze in a workout during naptime!": "作为一个忙碌的妈妈，我没有太多时间锻炼。15分钟快速锻炼非常适合我。我可以在午睡时间挤出时间锻炼！",
            
            "Bug: cannot share workouts": "Bug：无法分享锻炼",
            "When I try to share my workout progress on social media, the app crashes. I've tried multiple times and it always happens. This feature needs to be fixed.": "当我尝试在社交媒体上分享我的锻炼进度时，应用崩溃。我尝试了多次，总是发生这种情况。这个功能需要修复。",
            
            "Add Pilates workouts": "添加普拉提锻炼",
            "I do Pilates regularly and would love to see more Pilates workouts in the app. The current selection is very limited. Please add more variety!": "我定期做普拉提，希望看到应用中有更多普拉提锻炼。目前的选择非常有限。请添加更多种类！",
            
            "App crashes when trying to purchase": "尝试购买时应用崩溃",
            "When I try to upgrade to the premium version, the app crashes. I've tried on multiple devices and it's the same issue. I want to subscribe but can't!": "当我尝试升级到高级版本时，应用崩溃。我在多个设备上尝试过，都是同样的问题。我想订阅但不能！"
        }

    def translate(self, text: str, target_lang: str = "zh-CN") -> Optional[str]:
        if not text or not isinstance(text, str):
            return None
        
        text = text.strip()
        if not text:
            return None
        
        if text in self._cached_translations:
            return self._cached_translations[text]
        
        if text in self._sample_translations:
            translation = self._sample_translations[text]
            self._cached_translations[text] = translation
            return translation
        
        if HAS_TEXTBLOB:
            try:
                blob = TextBlob(text)
                translation = str(blob.translate(to=target_lang))
                if translation and translation != text:
                    self._cached_translations[text] = translation
                    return translation
            except Exception as e:
                print(f"TextBlob翻译失败: {e}")
        
        return None

    def translate_review(self, review: dict) -> dict:
        translated_review = review.copy()
        
        title_en = review.get("title", "")
        content_en = review.get("content", "")
        
        title_zh = self.translate(title_en)
        content_zh = self.translate(content_en)
        
        if title_zh:
            translated_review["title_zh"] = title_zh
        if content_zh:
            translated_review["content_zh"] = content_zh
        
        return translated_review

    def translate_reviews(self, reviews: list) -> list:
        return [self.translate_review(review) for review in reviews]