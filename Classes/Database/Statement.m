//
//  Statement.m
//  iBooks
//
//  Created by Jérôme Laheurte on 10/12/08.
//  Copyright 2008 __MyCompanyName__. All rights reserved.
//

#import "Statement.h"
#import "SQLite.h"

@implementation Statement

- initWithConnection:(SQLite *)cn andSQL:(NSString *)sql
{
	if (self = [super init])
	{
		if (sqlite3_prepare_v2([cn connection], [sql UTF8String], -1, &pReq, NULL) != SQLITE_OK)
		{
			@throw [NSException exceptionWithName:@"DatabaseError" reason:[cn errmsg] userInfo:nil];
		}
		
		connection = [cn retain];
	}
	
	return self;
}

- (void)dealloc
{
	sqlite3_finalize(pReq);
	[connection release];
	
	[super dealloc];
}

- (void)bindInteger:(NSInteger)value atIndex:(NSInteger)index
{
	if (sqlite3_bind_int(pReq, index, value) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[connection errmsg] userInfo:nil];
	}
}

- (void)bindString:(NSString *)string atIndex:(NSInteger)index
{
	if (sqlite3_bind_text(pReq, index, [string UTF8String], -1, NULL) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[connection errmsg] userInfo:nil];
	}
}

- (void)bindNullAtIndex:(NSInteger)index
{
	if (sqlite3_bind_null(pReq, index) != SQLITE_OK)
	{
		@throw [NSException exceptionWithName:@"DatabaseError" reason:[connection errmsg] userInfo:nil];
	}
}

- (void)exec
{
	int rc;

	while ((rc = sqlite3_step(pReq)) == SQLITE_ROW);
	
	if (rc != SQLITE_DONE)
		@throw [NSException exceptionWithName:@"DatabaseError" reason: [connection errmsg] userInfo:nil];

	if (sqlite3_reset(pReq) != SQLITE_OK)
		@throw [NSException exceptionWithName:@"DatabaseError" reason: [connection errmsg] userInfo:nil];
}

- (NSInteger)execWithTarget:(id)target action:(SEL)action
{
	NSInteger colCount = sqlite3_column_count(pReq);
	NSInteger rowCount = 0;

	// Find out column names

	NSMutableArray *colNames = [[NSMutableArray alloc] initWithCapacity:colCount];
	for (NSInteger i = 0; i < colCount; ++i)
	{
		[colNames addObject:[NSString stringWithUTF8String:sqlite3_column_name(pReq, i)]];
	}

	int rc;
	NSMutableDictionary *values = [[NSMutableDictionary alloc] initWithCapacity:colCount];

	while ((rc = sqlite3_step(pReq)) == SQLITE_ROW)
	{
		//NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];

		@try
		{
			[values removeAllObjects];

			for (int i = 0; i < colCount; ++i)
			{
				switch (sqlite3_column_type(pReq, i))
				{
					case SQLITE_INTEGER:
						[values setObject:[NSNumber numberWithInt:sqlite3_column_int(pReq, i)] forKey:[colNames objectAtIndex:i]];
						break;
					case SQLITE_TEXT:
						[values setObject:[NSString stringWithUTF8String:(char*)sqlite3_column_text(pReq, i)] forKey:[colNames objectAtIndex:i]];
						break;
					case SQLITE_NULL:
						break;
						// TODO: other types
					default:
						@throw [NSException exceptionWithName:@"DatabaseError" reason:@"Unknown column type" userInfo:nil];
				}
			}

			[target performSelector:action withObject:values];
		}
		@finally
		{
			//[pool release];
		}
		
		++rowCount;
	}
	
	[values release];
	[colNames release];

	if (rc != SQLITE_DONE)
		@throw [NSException exceptionWithName:@"DatabaseError" reason: [connection errmsg] userInfo:nil];

	if (sqlite3_reset(pReq) != SQLITE_OK)
		@throw [NSException exceptionWithName:@"DatabaseError" reason: [connection errmsg] userInfo:nil];
	
	return rowCount;
}

@end
