//
//  Configuration.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 17/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "Configuration.h"

static Configuration *_configuration = NULL;

@implementation Configuration

@synthesize showCompleted;
@synthesize iconPosition;
@synthesize compactTasks;
@synthesize confirmComplete;
@synthesize name;
@synthesize domain;

+ (Configuration *)configuration
{
	if (!_configuration)
		_configuration = [[Configuration alloc] init];
	return _configuration;
}

- init
{
	if (self = [super init])
	{
		NSUserDefaults *config = [NSUserDefaults standardUserDefaults];

		showCompleted = [config boolForKey:@"showcompleted"];
		iconPosition = [config integerForKey:@"iconposition"];
		compactTasks = [config boolForKey:@"compacttasks"];
		confirmComplete = [config boolForKey:@"confirmcomplete"];

		name = [[config stringForKey:@"name"] copy];
		domain = [[config stringForKey:@"domain"] copy];
	}
	
	return self;
}

- (void)dealloc
{
	[name release];
	[domain release];

	[super dealloc];
}

- (void)save
{
	NSUserDefaults *config = [NSUserDefaults standardUserDefaults];

	// Save only read-write properties
	if (name)
		[config setObject:name forKey:@"name"];
	if (domain)
		[config setObject:domain forKey:@"domain"];

	[config synchronize];
}

@end
