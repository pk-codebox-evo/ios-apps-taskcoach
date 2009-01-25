//
//  EndState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 25/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "EndState.h"
#import "Database.h"
#import "Network.h"
#import "SyncViewController.h"

@implementation EndState

- (void)activated
{
	[[Database connection] commit];

	[myNetwork release];

	myController.state = nil;
	[myController finished];
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[EndState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)networkDidEncounterError:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	// n/a
}

@end
