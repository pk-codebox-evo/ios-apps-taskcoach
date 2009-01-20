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
	}
	
	return self;
}

- (void)dealloc
{
	[super dealloc];
}

@end
