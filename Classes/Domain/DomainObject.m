//
//  DomainObject.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "DomainObject.h"
#import "Database.h"
#import "Statement.h"

@implementation DomainObject

@synthesize objectId;
@synthesize name;
@synthesize status;

- initWithId:(NSInteger)theId name:(NSString *)theName status:(NSInteger)theStatus
{
	if (self = [super init])
	{
		objectId = theId;
		name = [theName retain];
		status = theStatus;
	}
	
	return self;
}

- (void)dealloc
{
	[name release];
	
	[super dealloc];
}

- (void)setStatus:(NSInteger)newStatus
{
	switch (status)
	{
		case STATUS_NONE:
			status = newStatus;
			break;
		case STATUS_MODIFIED:
		case STATUS_NEW:
			if (newStatus == STATUS_DELETED)
				status = newStatus;
			break;
	}
}

- (void)delete
{
	Statement *req = [[Database connection] statementWithSQL:[NSString stringWithFormat:@"DELETE FROM %@ WHERE id=?", [self class]]];
	[req bindInteger:objectId atIndex:1];
	[req exec];
}

// Overriden setters to maintain the status

- (void)setName:(NSString *)newName
{
	if (![newName isEqualToString:name])
	{
		[name release];
		name = [newName retain];

		[self setStatus:STATUS_MODIFIED];
	}
}

@end
