//
//  InitialState.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 24/01/09.
//  Copyright 2009 __MyCompanyName__. All rights reserved.
//

#import "InitialState.h"
#import "Network.h"
#import "SyncViewController.h"
#import "ProtocolNegotiationState.h"
#import "Database.h"

// Initial state just waits for the connection to be established.

@implementation InitialState

- (void)activated
{
	myController.label.text = NSLocalizedString(@"Connecting...", @"Connecting title");
}

+ stateWithNetwork:(Network *)network controller:(SyncViewController *)controller
{
	return [[[InitialState alloc] initWithNetwork:network controller:controller] autorelease];
}

- (void)networkDidConnect:(Network *)network controller:(SyncViewController *)controller
{
	[[Database connection] begin];
	controller.state = [ProtocolNegotiationState stateWithNetwork:network controller:controller];
}

- (void)networkDidClose:(Network *)network controller:(SyncViewController *)controller
{
	// n/a
}

- (void)networkDidEncounterError:(Network *)network controller:(SyncViewController *)controller
{
	controller.state = nil;
	
	UIAlertView *view = [[UIAlertView alloc] initWithTitle:NSLocalizedString(@"Connection error", @"Connection error title")
												   message:NSLocalizedString(@"An error occurred while connecting to the remote host. Please check your settings. Also check that Task Coach is running on the remote host.", @"Connection error message")
												  delegate:controller cancelButtonTitle:NSLocalizedString(@"Abort", @"Connection error cancel button title") otherButtonTitles:nil];
	[view show];
	[view release];
	[network release];
}

- (void)network:(Network *)network didGetData:(NSData *)data controller:(SyncViewController *)controller
{
	// n/a
}

@end
