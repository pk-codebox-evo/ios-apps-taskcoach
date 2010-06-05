//
//  TaskCoachAppDelegate.m
//  TaskCoach
//
//  Created by Jérôme Laheurte on 14/01/09.
//  Copyright Jérôme Laheurte 2009. See COPYING for details.
//

#import "TaskCoachAppDelegate.h"
#import "PositionStore.h"
#import "CDDomainObject+Addons.h"
#import "CDTask.h"
#import "CDTask+Addons.h"
#import "i18n.h"

NSManagedObjectContext *getManagedObjectContext(void)
{
	return ((TaskCoachAppDelegate *)([UIApplication sharedApplication].delegate)).managedObjectContext;
}

@implementation TaskCoachAppDelegate

@synthesize window;
@synthesize mainController;

- (void)applicationDidFinishLaunching:(UIApplication *)application
{
	// These lines are just there so that gettext can retrieve strings
	// in the NIB. Remember to add a line here each time a translatable
	// string appears in a NIB.

	_("Cancel");
	_("Save");
	_("Categories");
	_("Sync");
	
	[window addSubview:mainController.view];
	[window makeKeyAndVisible];
	
	// Update date status for all objects
	NSFetchRequest *request = [[NSFetchRequest alloc] init];
	[request setEntity:[NSEntityDescription entityForName:@"CDTask" inManagedObjectContext:getManagedObjectContext()]];
	[request setPredicate:[NSPredicate predicateWithFormat:@"status != %d", STATUS_DELETED]];

	NSError *error;
	NSArray *tasks = [getManagedObjectContext() executeFetchRequest:request error:&error];
	if (tasks)
	{
		for (CDTask *task in tasks)
			[task computeDateStatus];

		if (![getManagedObjectContext() save:&error])
		{
			NSLog(@"Error saving: %@", [error localizedDescription]);
			UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not save tasks") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
			[alert show];
			[alert release];
		}
	}
	else
	{
		NSLog(@"Error fetching: %@", [error localizedDescription]);
		UIAlertView *alert = [[UIAlertView alloc] initWithTitle:_("Error") message:_("Could not load tasks") delegate:self cancelButtonTitle:_("OK") otherButtonTitles:nil];
		[alert show];
		[alert release];
	}
}

- (void)dealloc
{
    [managedObjectContext release];
    [managedObjectModel release];
    [persistentStoreCoordinator release];
    
	[mainController release];
    [window release];

    [super dealloc];
}

- (void)applicationWillTerminate:(UIApplication *)application
{
	UIViewController *ctrl = [mainController topViewController];
	
	if ([ctrl respondsToSelector:@selector(willTerminate)])
		[ctrl performSelector:@selector(willTerminate)];
	
	
	NSArray *cachesPaths = NSSearchPathForDirectoriesInDomains(NSCachesDirectory, NSUserDomainMask, YES);
	NSString *cachesDir = [cachesPaths objectAtIndex:0];
	
	NSFileManager *fileManager = [NSFileManager defaultManager];
	if (![fileManager fileExistsAtPath:cachesDir])
	{
		[fileManager createDirectoryAtPath:cachesDir attributes:nil];
	}
	
	NSString *path = [cachesDir stringByAppendingPathComponent:@"positions.store.v4"];
	[[PositionStore instance] save:path];

	[fileManager release];
	
	NSError *error;
	
	if (managedObjectContext != nil)
	{
        if ([managedObjectContext hasChanges] && ![managedObjectContext save:&error])
		{
			NSLog(@"Unresolved error %@, %@", error, [error userInfo]);
			exit(-1);  // Fail
        } 
    }
}

#pragma mark -
#pragma mark Core Data stack

/**
 Returns the managed object context for the application.
 If the context doesn't already exist, it is created and bound to the persistent store coordinator for the application.
 */
- (NSManagedObjectContext *) managedObjectContext
{
    if (managedObjectContext != nil)
	{
        return managedObjectContext;
    }
	
    NSPersistentStoreCoordinator *coordinator = [self persistentStoreCoordinator];
    if (coordinator != nil)
	{
        managedObjectContext = [[NSManagedObjectContext alloc] init];
        [managedObjectContext setPersistentStoreCoordinator: coordinator];
    }
	
    return managedObjectContext;
}


/**
 Returns the managed object model for the application.
 If the model doesn't already exist, it is created by merging all of the models found in the application bundle.
 */
- (NSManagedObjectModel *)managedObjectModel
{
    if (managedObjectModel != nil)
	{
        return managedObjectModel;
    }
	
	managedObjectModel = [[NSManagedObjectModel mergedModelFromBundles:nil] retain];    
	
    return managedObjectModel;
}


/**
 Returns the persistent store coordinator for the application.
 If the coordinator doesn't already exist, it is created and the application's store added to it.
 */
- (NSPersistentStoreCoordinator *)persistentStoreCoordinator
{
    if (persistentStoreCoordinator != nil)
	{
        return persistentStoreCoordinator;
    }

	NSString *path = [[self applicationDocumentsDirectory] stringByAppendingPathComponent: @"TaskCoachCD.sqlite"];
    NSURL *storeUrl = [NSURL fileURLWithPath: path];

	BOOL mustMigrate = ![[NSFileManager defaultManager] fileExistsAtPath:path];

	NSError *error;
    persistentStoreCoordinator = [[NSPersistentStoreCoordinator alloc] initWithManagedObjectModel: [self managedObjectModel]];
    if (![persistentStoreCoordinator addPersistentStoreWithType:NSSQLiteStoreType configuration:nil URL:storeUrl options:nil error:&error])
	{
		NSLog(@"Could not create store: %@", [error localizedDescription]);
    }    

	// XXXTODO: migrate existing data
	(void)mustMigrate;

    return persistentStoreCoordinator;
}


#pragma mark -
#pragma mark Application's documents directory

/**
 Returns the path to the application's documents directory.
 */
- (NSString *)applicationDocumentsDirectory
{
    NSArray *paths = NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, YES);
    NSString *basePath = ([paths count] > 0) ? [paths objectAtIndex:0] : nil;
    return basePath;
}

@end
